__all__ = [
    "TextSerializer",
    "MarkdownSerializer",
    "ExternalFilesManager",
    "SerializedFile",
    "EXTENSION_HIGHLIGHTING",
]

import os
import re
from base64 import b64encode
from contextlib import contextmanager
from dataclasses import dataclass, field
from itertools import chain
from mimetypes import guess_type
from pathlib import Path
from textwrap import indent
from typing import Any, Dict, Iterable, Iterator, Mapping, Optional, Type, Union
from urllib.parse import urlparse

from beet import DataPack, File, NamespaceFile, ResourcePack, TextFileBase
from beet.core.utils import normalize_string

EXTENSION_HIGHLIGHTING = {
    ".mcfunction": "mcfunction",
    ".json": "json",
    ".mcmeta": "json",
    ".fsh": "glsl",
    ".vsh": "glsl",
    ".glsl": "glsl",
}


@dataclass
class ExternalFilesManager:
    """Class responsible for saving external files."""

    directory: Path
    target: Path

    external_files: Dict[str, File[Any, Any]] = field(default_factory=dict)
    external_prefix: str = ""

    def __post_init__(self):
        if not self.external_prefix:
            prefix = os.path.relpath(self.directory, self.target.parent)
            prefix = prefix.replace(os.path.sep, "/")
            self.external_prefix = "" if prefix == "." else prefix.rstrip("/") + "/"

    def flush(self):
        """Save all the external files."""
        if self.external_files:
            self.directory.mkdir(parents=True, exist_ok=True)
            for filename, file_instance in self.external_files.items():
                file_instance.dump(self.directory, self.target.parent / filename)

    def __enter__(self) -> "ExternalFilesManager":
        return self

    def __exit__(self, *_):
        self.flush()


@dataclass
class SerializedFile:
    """Class representing a file emitted during the serialization process."""

    hint: str
    file_instance: File[Any, Any]

    filename: str = field(init=False)
    extension: str = field(init=False)
    content_type: str = field(init=False)

    def __post_init__(self):
        path = Path(urlparse(self.hint).path)
        self.extension = "".join(path.suffixes)
        self.filename = normalize_string(
            path.name[: -len(self.extension)] if self.extension else path.name
        )

        if not self.extension and isinstance(self.file_instance, NamespaceFile):
            self.extension = self.file_instance.extension

        self.content_type = (
            guess_type(f"{self.filename}{self.extension}")[0]
            or "application/octet-stream"
        )

    def get_local_path(
        self,
        external_files: Dict[str, File[Any, Any]],
        external_prefix: str = "",
    ) -> str:
        """Rename the file to prevent conflicts within the given environment."""
        while (
            path := f"{external_prefix}{self.filename}{self.extension}"
        ) in external_files:
            stem, _, number = self.filename.rpartition("_")
            if not number.isdigit():
                stem, number = self.filename, "0"
            self.filename = f"{stem}_{int(number) + 1}"
        return path

    def get_data_url(self):
        """Convert the file to a data url."""
        content = self.file_instance.ensure_serialized()
        return f"data:{self.content_type};base64,{b64encode(content).decode()}"

    def generate_link_target(
        self,
        external_files: Optional[Dict[str, File[Any, Any]]] = None,
        external_prefix: str = "",
    ) -> str:
        """Generate the link for including the file in a serialized document."""
        if external_files is None:
            return self.get_data_url()

        local_path = self.get_local_path(external_files, external_prefix)
        external_files[local_path] = self.file_instance
        return local_path


class TextSerializer:
    """Document serializer that outputs plain text."""

    escaped_regex: Optional["re.Pattern[str]"]

    def __init__(self):
        self.escaped_regex = None

    def get_escaped_regex(
        self, mapping: Mapping[Type[NamespaceFile], str]
    ) -> "re.Pattern[str]":
        """Create and return the escaped regex for the specified serialization mapping."""
        names = "|".join([*mapping.values(), "resource_pack", "data_pack"])
        pattern = rf"^(@+(?:{names})\b.*)$"

        if self.escaped_regex is None or self.escaped_regex.pattern != pattern:
            self.escaped_regex = re.compile(pattern, flags=re.MULTILINE)

        return self.escaped_regex

    def serialize(
        self,
        assets: ResourcePack,
        data: DataPack,
        mapping: Mapping[Type[NamespaceFile], str],
    ) -> str:
        """Return the serialized representation."""
        escaped_regex = self.get_escaped_regex(mapping)

        return "\n".join(
            (
                f"@{directive_name} {argument}\n{self.escape_fragment(content, escaped_regex)}"
                if isinstance(content := file_instance.ensure_serialized(), str)
                else f"@{directive_name}(base64) {argument}\n"
                + b64encode(content).decode()
                + "\n"
            )
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
                        extra_directive,
                        f"{namespace.directory}/{name}/{path}",
                        file_instance,
                    )
                    for name, namespace in pack.items()
                    for path, file_instance in namespace.extra.items()
                ),
                (
                    (
                        (
                            mapping[file_type],
                            f"{name}:{path}",
                            file_instance,
                        )
                        if file_type in mapping
                        else (
                            extra_directive,
                            f"{namespace.directory}/{name}/{'/'.join(file_type.scope)}/{path}{file_type.extension}",
                            file_instance,
                        )
                    )
                    for name, namespace in pack.items()
                    for file_type, container in namespace.items()
                    for path, file_instance in container.items()
                ),
            )
        )

    def escape_fragment(self, content: str, escaped_regex: "re.Pattern[str]") -> str:
        """Escape embedded directives."""
        return "".join(
            s.replace("@", "@@", 1) if i % 2 else s
            for i, s in enumerate(escaped_regex.split(content))
        )


class MarkdownSerializer:
    """Document serializer that outputs markdown and emits associated files."""

    flat: bool

    def __init__(self, flat: bool = False):
        self.flat = flat

    @contextmanager
    def use_flat_format(self, flat: bool = True):
        """Context manager for using the flat markdown format."""
        previous = self.flat
        self.flat = flat

        try:
            yield
        finally:
            self.flat = previous

    def serialize(
        self,
        assets: ResourcePack,
        data: DataPack,
        mapping: Mapping[Type[NamespaceFile], str],
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
                    title,
                    directive,
                    pack,
                    mapping,
                    external_files,
                    external_prefix,
                )
            )
            or "The data pack and resource pack are empty.\n"
        )

    def serialize_pack(
        self,
        title: str,
        pack_directive: str,
        pack: Union[DataPack, ResourcePack],
        mapping: Mapping[Type[NamespaceFile], str],
        external_files: Optional[Dict[str, File[Any, Any]]] = None,
        external_prefix: str = "",
    ) -> Iterator[str]:
        """Yield markdown chunks for the given pack."""
        yield f"## {title}"

        for path, file_instance in pack.extra.items():
            yield from self.format_serialized_file(
                self.serialize_file_instance(
                    pack_directive,
                    path,
                    file_instance,
                    external_files,
                    external_prefix,
                )
            )

        for name, namespace in pack.items():
            yield f"\n### {name}"

            for path, file_instance in namespace.extra.items():
                yield from self.format_serialized_file(
                    self.serialize_file_instance(
                        pack_directive,
                        f"{namespace.directory}/{name}/{path}",
                        file_instance,
                        external_files,
                        external_prefix,
                    )
                )

            for file_type, container in namespace.items():
                for path, file_instance in container.items():
                    if file_type in mapping:
                        yield from self.format_serialized_file(
                            self.serialize_file_instance(
                                mapping[file_type],
                                f"{name}:{path}",
                                file_instance,
                                external_files,
                                external_prefix,
                            )
                        )
                    else:
                        yield from self.format_serialized_file(
                            self.serialize_file_instance(
                                pack_directive,
                                f"{namespace.directory}/{name}/{'/'.join(file_type.scope)}/{path}{file_type.extension}",
                                file_instance,
                                external_files,
                                external_prefix,
                            )
                        )
        yield ""

    def format_serialized_file(self, chunks: Iterable[str]) -> Iterator[str]:
        """Format the markdown chunks for serializing file instances."""
        if self.flat:
            yield ""
        else:
            chunks = [indent(chunk, "  ") for chunk in chunks]
            chunks[0] = "\n-" + chunks[0][1:]
        yield from chunks

    def serialize_file_instance(
        self,
        directive: str,
        argument: str,
        file_instance: Union[File[Any, Any], NamespaceFile],
        external_files: Optional[Dict[str, File[Any, Any]]] = None,
        external_prefix: str = "",
    ) -> Iterator[str]:
        """Yield markdown chunks for including the given file instance."""
        serialized_file = SerializedFile(argument, file_instance)

        if isinstance(file_instance, TextFileBase):
            content = file_instance.text

            if not content.endswith("\n"):
                directive += "(strip_final_newline)"
                content += "\n"

            yield f"`@{directive} {argument}`"
            if not self.flat:
                yield "\n<details>"
            yield "\n```" + EXTENSION_HIGHLIGHTING.get(serialized_file.extension, "")
            yield content + "```"
            if not self.flat:
                yield "\n</details>"

            return

        target = serialized_file.generate_link_target(external_files, external_prefix)

        if serialized_file.content_type.startswith("image/"):
            yield f"`@{directive} {argument}`"
            if not self.flat:
                yield "\n<details>"
            yield f"\n![{directive}{serialized_file.extension}]({target})"
            if not self.flat:
                yield "\n</details>"
        else:
            yield f"[`@{directive} {argument}`]({target})"
