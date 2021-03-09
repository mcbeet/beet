__all__ = [
    "Document",
]


from dataclasses import InitVar, dataclass, field
from pathlib import Path
from typing import Any, Dict, Literal, MutableMapping, Optional, Tuple, Union, overload

from beet import Cache, Context, DataPack, File, ResourcePack
from beet.core.utils import FileSystemPath, extra_field

from .directive import Directive, RequireDirective, get_builtin_directives
from .extract import MarkdownExtractor, TextExtractor
from .serialize import ExternalFilesManager, MarkdownSerializer, TextSerializer


@dataclass
class Document:
    """Class representing a lectern document."""

    ctx: InitVar[Optional[Context]] = None
    path: InitVar[Optional[FileSystemPath]] = None
    text: InitVar[Optional[str]] = None
    markdown: InitVar[Optional[str]] = None
    cache: InitVar[Optional[Cache]] = None
    external_files: InitVar[Optional[FileSystemPath]] = None

    assets: ResourcePack = field(default_factory=ResourcePack)
    data: DataPack = field(default_factory=DataPack)

    directives: MutableMapping[str, Directive] = extra_field(
        default_factory=get_builtin_directives
    )

    text_extractor: TextExtractor = extra_field(default_factory=TextExtractor)
    markdown_extractor: MarkdownExtractor = extra_field(
        default_factory=MarkdownExtractor
    )

    text_serializer: TextSerializer = extra_field(default_factory=TextSerializer)
    markdown_serializer: MarkdownSerializer = extra_field(
        default_factory=MarkdownSerializer
    )

    def __post_init__(
        self,
        ctx: Optional[Context],
        path: Optional[FileSystemPath] = None,
        text: Optional[str] = None,
        markdown: Optional[str] = None,
        cache: Optional[Cache] = None,
        external_files: Optional[FileSystemPath] = None,
    ):
        if ctx:
            self.assets = ctx.assets
            self.data = ctx.data
            self.directives["require"] = RequireDirective(ctx)
            if cache is None:
                cache = ctx.cache["lectern"]
        if cache:
            self.text_extractor.cache = cache
            self.markdown_extractor.cache = cache
        if path:
            self.load(path)
        if text:
            self.add_text(text)
        if markdown:
            self.add_markdown(markdown, external_files)

    def load(self, path: FileSystemPath):
        """Load and extract fragments from the file at the specified location."""
        path = Path(path).resolve()
        if path.suffix == ".md":
            self.add_markdown(path.read_text(), external_files=path.parent)
        else:
            self.add_text(path.read_text())

    def add_text(self, source: str):
        """Extract pack fragments from plain text."""
        assets, data = self.text_extractor.extract(source, self.directives)
        self.assets.merge(assets)
        self.data.merge(data)

    def add_markdown(
        self,
        source: str,
        external_files: Optional[FileSystemPath] = None,
    ):
        """Extract pack fragments from markdown."""
        assets, data = self.markdown_extractor.extract(
            source=source,
            directives=self.directives,
            external_files=external_files,
        )
        self.assets.merge(assets)
        self.data.merge(data)

    def get_text(self) -> str:
        """Turn the data pack and the resource pack into text."""
        return self.text_serializer.serialize(self.assets, self.data)

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
    ):
        """Save the serialized document at the specified location."""
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
