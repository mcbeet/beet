__all__ = [
    "Extractor",
    "TextExtractor",
    "EmbeddedExtractor",
    "MarkdownExtractor",
]


import re
from itertools import islice
from typing import Dict, Iterable, Mapping, Optional, Tuple

from beet import DataPack, ResourcePack
from beet.core.utils import FileSystemPath

from .directive import Directive
from .fragment import Fragment


class Extractor:
    """Base class for extractors."""

    directives: Dict[str, Directive]
    regex: Optional["re.Pattern[str]"]

    def __init__(self):
        self.directives = {}
        self.regex = None

    def generate_regex(self) -> str:
        """Return a regex that can match the current directives."""
        names = "|".join(name for name in self.directives)
        modifier = r"(?:\((?P<modifier>[^)]+)\)|\b)"
        arguments = r"(?P<arguments>.*)"
        return f"@(?P<name>{names}){modifier}{arguments}"

    def compile_regex(self, regex: str) -> "re.Pattern[str]":
        """Return the compiled pattern for the directive regex."""
        return re.compile(f"^{regex}$", flags=re.MULTILINE)

    def get_regex(self, directives: Mapping[str, Directive]) -> "re.Pattern[str]":
        """Create and return the regex for the specified directives."""
        directives = dict(directives)

        if self.regex is None or self.directives != directives:
            self.directives = directives
            self.regex = self.compile_regex(self.generate_regex())

        return self.regex


class TextExtractor(Extractor):
    """Extractor for plain text files."""

    def extract(
        self,
        source: str,
        directives: Mapping[str, Directive],
    ) -> Tuple[ResourcePack, DataPack]:
        """Turn text into a resource pack and a data pack."""
        assets, data = ResourcePack(), DataPack()

        tokens = self.get_regex(directives).split(source + "\n")

        for directive_name, fragment in self.generate_fragments(tokens):
            self.directives[directive_name](fragment, assets, data)

        return assets, data

    def generate_fragments(self, tokens: Iterable[str]):
        """Yield pack fragments from a token stream."""
        it = iter(tokens)
        next(it)

        while True:
            try:
                directive, modifier, arguments, content = islice(it, 4)
            except ValueError:
                return
            else:
                content = content.partition("\n")[-1]
                yield directive, Fragment(
                    modifier,
                    arguments.split(),
                    content[:-1] if content.endswith("\n") else content,
                )


class EmbeddedExtractor(TextExtractor):
    """Extractor for directives embedded in markdown code blocks."""

    def generate_regex(self) -> str:
        return r"(?://|#)\s*" + super().generate_regex()


class MarkdownExtractor(Extractor):
    """Extractor for markdown files."""

    def __init__(self):
        super().__init__()
        self.embedded_extractor = EmbeddedExtractor()

    def extract(
        self,
        source: str,
        directives: Mapping[str, Directive],
        files: Optional[FileSystemPath] = None,
    ) -> Tuple[ResourcePack, DataPack]:
        """Turn markdown into a resource pack and a data pack."""
        assets, data = ResourcePack(), DataPack()
        return assets, data
