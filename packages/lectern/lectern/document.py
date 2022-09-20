__all__ = [
    "Document",
]


import re
from dataclasses import InitVar, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple, Union, overload

from beet import Cache, Context, DataPack, File, ResourcePack
from beet.core.utils import FileSystemPath, extra_field

from .directive import DirectiveRegistry
from .extract import FragmentLoader, MarkdownExtractor, TextExtractor
from .serialize import (
    ExternalFilesManager,
    MarkdownSerializer,
    TextSerializer,
    snapshot_serialization_filter,
)


@dataclass
class Document:
    """Class representing a lectern document."""

    ctx: InitVar[Optional[Context]] = None
    path: InitVar[Optional[FileSystemPath]] = None
    source: InitVar[Optional[str]] = None
    text: InitVar[Optional[str]] = None
    markdown: InitVar[Optional[str]] = None
    cache: InitVar[Optional[Cache]] = None
    external_files: InitVar[Optional[FileSystemPath]] = None

    assets: ResourcePack = field(default_factory=ResourcePack)
    data: DataPack = field(default_factory=DataPack)

    loaders: List[FragmentLoader] = extra_field(default_factory=list)
    directives: DirectiveRegistry = extra_field(default_factory=DirectiveRegistry)

    text_extractor: TextExtractor = extra_field(default_factory=TextExtractor)
    markdown_extractor: MarkdownExtractor = extra_field(
        default_factory=MarkdownExtractor
    )

    text_serializer: TextSerializer = extra_field(default_factory=TextSerializer)
    markdown_serializer: MarkdownSerializer = extra_field(
        default_factory=MarkdownSerializer
    )

    markdown_sniffer: "re.Pattern[str]" = extra_field(
        default=re.compile(
            r"^[ \t]*```|^[ \t]*<!--|^[ \t]*-->|^[ \t]*[*-]?[ \t]*\[?[ \t]*`@[a-z0-9_]{3,}",
            re.MULTILINE,
        )
    )

    def __post_init__(
        self,
        ctx: Optional[Context],
        path: Optional[FileSystemPath] = None,
        source: Optional[str] = None,
        text: Optional[str] = None,
        markdown: Optional[str] = None,
        cache: Optional[Cache] = None,
        external_files: Optional[FileSystemPath] = None,
    ):
        if ctx:
            self.assets = ctx.assets
            self.data = ctx.data
            if cache is None:
                cache = ctx.cache["lectern"]

        if cache:
            self.text_extractor.cache = cache
            self.markdown_extractor.cache = cache

        self.directives.assets = self.assets
        self.directives.data = self.data

        if path:
            self.load(path)
        if source:
            self.add(source)
        if text:
            self.add_text(text)
        if markdown:
            self.add_markdown(markdown, external_files)

    def load(self, path: FileSystemPath):
        """Load and extract fragments from the file at the specified location."""
        path = Path(path).resolve()
        self.add(path.read_text(), external_files=path.parent)

    def add(
        self,
        source: str,
        external_files: Optional[FileSystemPath] = None,
    ) -> bool:
        """Extract pack fragments from source."""
        if self.markdown_sniffer.search(source):
            return self.add_markdown(source, external_files)
        else:
            return self.add_text(source)

    def add_text(self, source: str) -> bool:
        """Extract pack fragments from plain text."""
        assets, data = self.text_extractor.extract(
            source=source,
            directives=self.directives.resolve(),
            loaders=self.loaders,
        )
        non_empty = bool(assets or data)
        self.assets.merge(assets)
        self.data.merge(data)
        return non_empty

    def add_markdown(
        self,
        source: str,
        external_files: Optional[FileSystemPath] = None,
    ) -> bool:
        """Extract pack fragments from markdown."""
        assets, data = self.markdown_extractor.extract(
            source=source,
            directives=self.directives.resolve(),
            loaders=self.loaders,
            external_files=external_files,
        )
        non_empty = bool(assets or data)
        self.assets.merge(assets)
        self.data.merge(data)
        return non_empty

    def get_text(self) -> str:
        """Turn the data pack and the resource pack into text."""
        return self.text_serializer.serialize(
            assets=self.assets,
            data=self.data,
            mapping=self.directives.resolve().get_serialization_mapping(),
        )

    @overload
    def get_markdown(
        self,
        emit_external_files: Literal[True],
        prefix: str = "",
    ) -> Tuple[str, Dict[str, File[Any, Any]]]:
        ...

    @overload
    def get_markdown(self, emit_external_files: Literal[False] = False) -> str:
        ...

    def get_markdown(
        self,
        emit_external_files: bool = False,
        prefix: str = "",
    ) -> Union[str, Tuple[str, Dict[str, File[Any, Any]]]]:
        """Turn the data pack and the resource pack into markdown."""
        external_files: Optional[Dict[str, File[Any, Any]]] = (
            {} if emit_external_files else None
        )

        content = self.markdown_serializer.serialize(
            assets=self.assets,
            data=self.data,
            mapping=self.directives.resolve().get_serialization_mapping(),
            external_files=external_files,
            external_prefix=prefix,
        )

        if external_files is None:
            return content
        else:
            return content, external_files

    def save(
        self,
        path: FileSystemPath,
        external_files: Optional[FileSystemPath] = None,
        snapshot: bool = False,
    ):
        """Save the serialized document at the specified location."""
        if snapshot:
            self.text_serializer.pack_filter = snapshot_serialization_filter
            self.markdown_serializer.flat = True
            self.markdown_serializer.pack_filter = snapshot_serialization_filter

        path = Path(path).resolve()

        if path.suffix == ".md":
            if external_files:
                with ExternalFilesManager(
                    Path(external_files).resolve(), path
                ) as manager:
                    content, files = self.get_markdown(
                        emit_external_files=True,
                        prefix=manager.external_prefix,
                    )
                    manager.external_files.update(files)
            else:
                content = self.get_markdown()
        else:
            content = self.get_text()

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
