__all__ = [
    "TextSerializer",
    "MarkdownSerializer",
    "NAMESPACED_RESOURCE_DIRECTIVES",
    "EXTENSION_HIGHLIGHTING",
]

from base64 import b64encode
from itertools import chain
from mimetypes import guess_type
from pathlib import Path
from textwrap import indent
from typing import Any, Dict, Iterator, Optional, Union

from beet import DataPack, File, ResourcePack, TextFileBase
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

    def serialize(
        self,
        assets: ResourcePack,
        data: DataPack,
        external_files: Optional[Dict[str, File[Any, Any]]] = None,
        external_prefix: str = "",
    ) -> str:
        """Return the serialized representation and the files emitted in the process."""
        return "# Lectern snapshot\n\n" + (
            "\n".join(
                text
                for title, directive, pack in [
                    ("Data pack", "data_pack", data),
                    ("Resource pack", "resource_pack", assets),
                ]
                if pack
                for text in self.serialize_pack(
                    title, directive, pack, external_files, external_prefix
                )
            )
            or "The data pack and resource pack are empty.\n"
        )

    def serialize_pack(
        self,
        title: str,
        pack_directive: str,
        pack: Union[DataPack, ResourcePack],
        external_files: Optional[Dict[str, File[Any, Any]]],
        external_prefix: str = "",
    ) -> Iterator[str]:
        """Yield markdown chunks for the given pack."""
        yield f"## {title}"

        for path, file_instance in pack.extra.items():
            yield from self.serialize_file_instance(
                pack_directive, path, file_instance, external_files, external_prefix
            )

        for name, namespace in pack.items():
            yield f"\n### {name}"

            for file_type, container in namespace.items():
                directive_name = NAMESPACED_RESOURCE_DIRECTIVES[file_type]

                for path, file_instance in container.items():
                    yield from self.serialize_file_instance(
                        directive_name,
                        f"{name}:{path}",
                        file_instance,
                        external_files,
                        external_prefix,
                    )

        yield ""

    def serialize_file_instance(
        self,
        directive: str,
        argument: str,
        file_instance: Union[File[Any, Any], NamespaceFile],
        external_files: Optional[Dict[str, File[Any, Any]]],
        external_prefix: str = "",
    ) -> Iterator[str]:
        """Yield markdown chunks for including the given file instance."""
        if directive in ["data_pack", "resource_pack"]:
            filename = Path(argument).name
            extension = "".join(Path(filename).suffixes)
            filename = filename[: -len(extension)]
        elif isinstance(file_instance, NamespaceFile):
            filename = Path(argument.rpartition(":")[-1]).name
            extension = file_instance.extension
        else:
            filename = f"{directive}_data"
            extension = ""

        if isinstance(file_instance, TextFileBase):
            content = file_instance.text

            if not content.endswith("\n"):
                directive += "(strip_final_newline)"
                content += "\n"

            yield f"\n- `@{directive} {argument}`"
            yield "\n  <details>"
            yield "\n  ```" + EXTENSION_HIGHLIGHTING.get(extension, "")
            yield indent(content, "  ") + "  ```"
            yield "\n  </details>"

            return

        if external_files is None:
            content = file_instance.ensure_serialized()
            content_type = (
                guess_type(f"{filename}{extension}")[0] or "application/octet-stream"
            )
            url = f"data:{content_type};base64,{b64encode(content).decode()}"

        else:
            while (url := f"{external_prefix}{filename}{extension}") in external_files:
                stem, _, number = filename.rpartition("_")
                if not number.isdigit():
                    stem, number = filename, "0"
                filename = f"{stem}_{int(number) + 1}"

            content_type = guess_type(url)[0] or "application/octet-stream"
            external_files[url] = file_instance

        if content_type.startswith("image/"):
            yield f"\n- `@{directive} {argument}`"
            yield "\n  <details>"
            yield f"\n  ![{directive}{extension}]({url})"
            yield "\n  </details>"
        else:
            yield f"\n- [`@{directive} {argument}`]({url})"
