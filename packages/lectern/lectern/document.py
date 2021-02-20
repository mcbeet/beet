__all__ = [
    "Document",
]


from dataclasses import InitVar, dataclass, field
from pathlib import Path
from typing import MutableMapping, Optional

from beet import Context, DataPack, ResourcePack
from beet.core.utils import FileSystemPath, extra_field

from .directive import Directive, get_builtin_directives
from .extract import MarkdownExtractor, TextExtractor
from .serialize import MarkdownSerializer, TextSerializer


@dataclass
class Document:
    """Class representing a lectern document."""

    ctx: InitVar[Optional[Context]] = None

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

    def __post_init__(self, ctx: Optional[Context]):
        if ctx:
            self.assets = ctx.assets
            self.data = ctx.data

    def add_text(self, source: str):
        """Extract pack fragments from plain text."""
        assets, data = self.text_extractor.extract(source, self.directives)

        self.assets.merge(assets)
        self.data.merge(data)

    def add_markdown(self, source: str, files: Optional[FileSystemPath] = None):
        """Extract pack fragments from markdown."""
        assets, data = self.markdown_extractor.extract(source, self.directives, files)

        self.assets.merge(assets)
        self.data.merge(data)

    def serialize(self, as_text: bool = False) -> str:
        """Serialize the inner data pack and the resource pack."""
        return (
            self.text_serializer.serialize(self.assets, self.data)
            if as_text
            else self.markdown_serializer.serialize_and_emit_files(
                self.assets, self.data
            )[0]
        )

    def save(self, path: FileSystemPath, files: Optional[FileSystemPath] = None):
        """Save the serialized document at the specified location."""
        path = Path(path).resolve()

        if path.suffix == ".md":
            data, emit = self.markdown_serializer.serialize_and_emit_files(
                self.assets, self.data
            )
            if files:
                files = Path(files).resolve()
                files.parent.mkdir(parents=True, exist_ok=True)
                for key, value in emit.items():
                    value.dump(files, key)
        else:
            data = self.text_serializer.serialize(self.assets, self.data)

        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(data)
