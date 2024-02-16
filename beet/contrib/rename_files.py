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
from typing import Any, Callable, List, Optional, Type, Union, cast

from pydantic.v1 import BaseModel

from beet import (
    Context,
    DataPack,
    File,
    ListOption,
    NamespaceFile,
    PackFilesOption,
    PackMatchOption,
    PackQuery,
    PluginOptions,
    PreparedPackFilesQuery,
    PreparedPackMatchQuery,
    ResourcePack,
    TemplateManager,
    configurable,
)
from beet.contrib.find_replace import RenderSubstitutionOption, TextSubstitutionOption

logger = logging.getLogger(__name__)


class TextRenameOption(TextSubstitutionOption):
    match: Optional[PackMatchOption] = None


class RenderRenameOption(RenderSubstitutionOption):
    match: Optional[PackMatchOption] = None


class RenameOption(BaseModel):
    __root__: ListOption[Union[TextRenameOption, RenderRenameOption]] = ListOption()

    def compile(
        self,
        query: PackQuery[Union[ResourcePack, DataPack]],
        template: TemplateManager,
    ) -> List["RenameFilesHandler"]:
        return [
            RenameFilesHandler(
                (
                    query.prepare(opts.match)
                    if opts.match is not None
                    else query.prepare(PackFilesOption.parse_obj({"": opts.find}))
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
    query: Union[
        PreparedPackFilesQuery[Union[ResourcePack, DataPack]],
        PreparedPackMatchQuery[Union[ResourcePack, DataPack]],
    ]
    substitute: Callable[[str], str]

    def __call__(self):
        if isinstance(self.query, PreparedPackMatchQuery):
            for entries in self.query.select().values():
                for (path, file_instance), (pack, _) in entries.items():
                    self.handle_path_for_namespace_file(pack, file_instance, path)  # type: ignore
        else:
            file_types = tuple(
                cast(Type[File[Any, Any]], file_type)
                for pack in self.query.packs
                for file_type in pack.get_file_types()
            )
            for (filename, file_instance), (pack, _) in self.query.select().items():
                if isinstance(file_instance, file_types):
                    self.handle_filename_for_namespace_file(pack, file_instance, filename)  # type: ignore
                else:
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
            file_type.snake_name,
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
        for handler in rename_option.compile(ctx.query.from_pack(pack), ctx.template):
            handler()
