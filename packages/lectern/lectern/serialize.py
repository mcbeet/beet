__all__ = [
    "TextSerializer",
    "MarkdownSerializer",
    "NAMESPACED_RESOURCE_DIRECTIVES",
]

from itertools import chain
from pathlib import Path
from textwrap import indent
from typing import Any, Dict, Iterator, Tuple, Union

from beet import DataPack, File, ResourcePack
from beet.library.base import NamespaceFile

from .directive import NamespacedResourceDirective, get_builtin_directives

NAMESPACED_RESOURCE_DIRECTIVES = {
    directive.file_type: directive_name
    for directive_name, directive in get_builtin_directives().items()
    if isinstance(directive, NamespacedResourceDirective)
}

EXTENSION_HIGHLIGHTING = {
    ".mcfunction": "mcfunction",
    ".json": "json",
    ".mcmeta": "json",
}


class TextSerializer:
    """Document serializer that outputs plain text."""

    def serialize(self, assets: ResourcePack, data: DataPack) -> str:
        """Return the serialized representation."""
        return "\n".join(
            f"@{directive_name} {argument}\n{content}"
            for pack, extra_directive in [
                (assets, "resource_pack"),
                (data, "data_pack"),
            ]
            if pack
            for directive_name, argument, file_instance in chain(
                (
                    (extra_directive, path, file_instance)
                    for path, file_instance in pack.extra.items()
                ),
                (
                    (
                        NAMESPACED_RESOURCE_DIRECTIVES[file_type],
                        f"{name}:{path}",
                        file_instance,
                    )
                    for name, namespace in pack.items()
                    for file_type, container in namespace.items()
                    for path, file_instance in container.items()
                ),
            )
            if isinstance(content := file_instance.ensure_serialized(), str)
        )


class MarkdownSerializer:
    """Document serializer that outputs markdown and emits associated files."""

    def serialize_and_emit_files(
        self,
        assets: ResourcePack,
        data: DataPack,
    ) -> Tuple[str, Dict[str, File[Any, Any]]]:
        """Return the serialized representation and the files emitted in the process."""
        files: Dict[str, File[Any, Any]] = {}

        content = (
            "\n".join(
                text
                for title, directive, pack in [
                    ("Data pack", "data_pack", data),
                    ("Resource pack", "resource_pack", assets),
                ]
                if pack
                for text in self.serialize_pack(title, directive, pack, files)
            )
            or "The data pack and resource pack are empty.\n"
        )

        return "# Lectern snapshot\n\n" + (content), files

    def serialize_pack(
        self,
        title: str,
        pack_directive: str,
        pack: Union[DataPack, ResourcePack],
        files: Dict[str, File[Any, Any]],
    ) -> Iterator[str]:
        """Yield markdown chunks for the given pack."""
        yield f"## {title}"

        yield "\n### Files"

        for path, file_instance in pack.extra.items():
            yield from self.serialize_file_instance(
                pack_directive, path, file_instance, files
            )

        for name, namespace in pack.items():
            yield f"\n### {name.title()} namespace"

            for file_type, container in namespace.items():
                directive_name = NAMESPACED_RESOURCE_DIRECTIVES[file_type]

                for path, file_instance in container.items():
                    yield from self.serialize_file_instance(
                        directive_name, f"{name}:{path}", file_instance, files
                    )

        yield ""

    def serialize_file_instance(
        self,
        directive: str,
        argument: str,
        file_instance: Union[File[Any, Any], NamespaceFile],
        files: Dict[str, File[Any, Any]],
    ) -> Iterator[str]:
        """Yield markdown chunks for including the given file instance."""
        content = file_instance.ensure_serialized()

        if isinstance(content, str):
            extension = (
                file_instance.extension
                if isinstance(file_instance, NamespaceFile)
                else Path(argument).suffix
            )

            if not content.endswith("\n"):
                directive += "(strip_final_newline)"
                content += "\n"

            yield f"\n- `@{directive} {argument}`"
            yield "\n  ```" + EXTENSION_HIGHLIGHTING.get(extension, "")
            yield indent(content, "  ") + "  ```"
