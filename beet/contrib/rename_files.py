"""Plugin for renaming files."""


__all__ = [
    "rename_files",
    "RenameFilesHandler",
    "RenameFilesOptions",
    "RenameOption",
    "TextRenameOption",
    "RenderRenameOption",
]


import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Type, Union, cast

from pydantic import BaseModel

from beet import (
    Context,
    DataPack,
    File,
    ListOption,
    NamespaceFile,
    PackSelector,
    PathSpecOption,
    PluginOptions,
    ResourcePack,
    TemplateManager,
    configurable,
)
from beet.contrib.find_replace import RenderSubstitutionOption, TextSubstitutionOption
from beet.core.utils import snake_case

logger = logging.getLogger(__name__)


class TextRenameOption(TextSubstitutionOption):
    match: Optional[Union[PathSpecOption, Dict[str, PathSpecOption]]] = None


class RenderRenameOption(RenderSubstitutionOption):
    match: Optional[Union[PathSpecOption, Dict[str, PathSpecOption]]] = None


class RenameOption(BaseModel):
    __root__: ListOption[Union[TextRenameOption, RenderRenameOption]] = ListOption()

    def compile(self, template: TemplateManager) -> List["RenameFilesHandler"]:
        return [
            RenameFilesHandler(
                (
                    PackSelector.from_options(match=opts.match, template=template)
                    if opts.match
                    else PackSelector.from_options(files=opts.find, template=template)
                ),
                opts.compile(template),
            )
            for opts in self.__root__.entries()
        ]


class RenameFilesOptions(PluginOptions):
    resource_pack: RenameOption = RenameOption()
    data_pack: RenameOption = RenameOption()


@dataclass
class RenameFilesHandler:
    pack_selector: PackSelector
    substitute: Callable[[str], str]

    def __call__(self, pack: Union[ResourcePack, DataPack]):
        namespace_file_types = {
            cast(Type[File[Any, Any]], file_type)
            for file_type in pack.resolve_scope_map().values()
        }

        files = self.pack_selector.select_files(pack)

        for file_instance, (filename, path) in files.items():
            if type(file_instance) in namespace_file_types:
                if path:
                    self.handle_path_for_namespace_file(pack, file_instance, path)  # type: ignore
                elif filename:
                    self.handle_filename_for_namespace_file(pack, file_instance, filename)  # type: ignore
            elif filename:
                self.handle_filename(pack, file_instance, filename)

    def handle_path_for_namespace_file(
        self,
        pack: Union[ResourcePack, DataPack],
        file_instance: NamespaceFile,
        path: str,
    ):
        dest = self.substitute(path)
        file_type = type(file_instance)
        del pack[file_type][path]
        pack[file_type][dest] = file_instance

    def handle_filename_for_namespace_file(
        self,
        pack: Union[ResourcePack, DataPack],
        file_instance: NamespaceFile,
        filename: str,
    ):
        dest = self.substitute(filename)
        file_type = type(file_instance)
        prefix = "".join(f"{d}/" for d in file_type.scope)

        _, namespace, path = filename.split("/", 2)

        if len(dest_parts := dest.split("/", 2)) == 3:
            dest_directory, dest_namespace, dest_path = dest_parts
            if (
                pack.namespace_type.directory == dest_directory
                and dest_path.startswith(prefix)
                and dest_path.endswith(file_type.extension)
            ):
                s = slice(len(prefix), -len(file_type.extension))
                del pack[namespace][file_type][path[s]]
                pack[dest_namespace][file_type][dest_path[s]] = file_instance
                return

        logger.warning(
            'Invalid %s destination "%s".',
            snake_case(file_type.__name__),
            dest,
            extra={"annotate": filename},
        )

    def handle_filename(
        self,
        pack: Union[ResourcePack, DataPack],
        file_instance: File[Any, Any],
        filename: str,
    ):
        dest = self.substitute(filename)

        namespace_extra = False

        if len(parts := filename.split("/", 2)) == 3:
            directory, namespace, path = parts
            if pack.namespace_type.directory == directory:
                if pack[namespace].extra.pop(path, None):
                    namespace_extra = True

        if not namespace_extra:
            del pack.extra[filename]

        if len(parts := dest.split("/", 2)) == 3:
            directory, namespace, path = parts
            if pack.namespace_type.directory == directory:
                pack[namespace].extra[path] = file_instance
                return

        pack.extra[filename] = file_instance


def beet_default(ctx: Context):
    ctx.require(rename_files)


@configurable(validator=RenameFilesOptions)
def rename_files(ctx: Context, opts: RenameFilesOptions):
    """Plugin for renaming files."""
    for pack, rename_option in zip(ctx.packs, [opts.resource_pack, opts.data_pack]):
        for handler in rename_option.compile(ctx.template):
            handler(pack)
