__all__ = [
    "MarkdownPrefetcher",
]


from collections.abc import Mapping
from dataclasses import InitVar, dataclass, field
from pathlib import Path
from typing import Any

from beet import BinaryFile, Cache, File
from beet.core.utils import FileSystemPath

from .directive import Directive, DirectiveRegistry
from .extract import MarkdownExtractor
from .fragment import Fragment
from .serialize import ExternalFilesManager, SerializedFile


@dataclass
class MarkdownPrefetcher:
    """Prefetcher that rewrites markdown links."""

    cache: InitVar[Cache | None] = None

    extractor: MarkdownExtractor = field(default_factory=MarkdownExtractor)

    def __post_init__(self, cache: Cache | None):
        if cache is not None:
            self.extractor.cache = cache

    def process_file(
        self,
        path: FileSystemPath,
        output: FileSystemPath,
        directives: Mapping[str, Directive] | None = None,
        external_files: FileSystemPath | None = None,
    ):
        """Prefetch urls in the specified document."""
        if directives is None:
            directives = DirectiveRegistry().resolve()

        path = Path(path).resolve()
        output = Path(output).resolve()

        if external_files:
            with ExternalFilesManager(
                Path(external_files).resolve(), output
            ) as manager:
                content = self.prefetch_urls(
                    path.read_text(),
                    directives,
                    manager.external_files,
                    manager.external_prefix,
                )
        else:
            content = self.prefetch_urls(path.read_text(), directives)

        output.write_text(content)

    def prefetch_urls(
        self,
        source: str,
        directives: Mapping[str, Directive],
        external_files: dict[str, File[Any, Any]] | None = None,
        external_prefix: str = "",
    ) -> str:
        """Replace remote urls in the input by data urls or links to local files."""
        return "".join(
            (
                self.rewrite_fragment(
                    text,
                    fragment.url,
                    fragment,
                    external_files,
                    external_prefix,
                )
                if fragment and fragment.url
                else text
            )
            for text, fragment in self.extractor.split(source, directives)
        )

    def rewrite_fragment(
        self,
        text: str,
        url: str,
        fragment: Fragment,
        external_files: dict[str, File[Any, Any]] | None = None,
        external_prefix: str = "",
    ) -> str:
        """Prefetch the url and return the modified fragment."""
        serialized_file = SerializedFile(
            hint=fragment.arguments[0] if fragment.arguments else url,
            file_instance=fragment.as_file(BinaryFile),
        )

        return text.replace(
            url, serialized_file.generate_link_target(external_files, external_prefix)
        )
