__all__ = [
    "Extractor",
    "TextExtractor",
    "EmbeddedExtractor",
    "MarkdownExtractor",
]


import re
from itertools import islice
from typing import Dict, Iterable, Iterator, List, Mapping, Optional, Tuple, Union

from beet import DataPack, ResourcePack
from beet.core.utils import FileSystemPath
from markdown_it import MarkdownIt
from markdown_it.token import Token

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
        modifier = r"(?:\((?P<modifier>[^)]*)\)|\b)"
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

    def extract(
        self,
        source: str,
        directives: Mapping[str, Directive],
    ) -> Tuple[ResourcePack, DataPack]:
        """Extract a resource pack and a data pack."""
        return self.apply_directives(
            directives, self.parse_fragments(source, directives)
        )

    def apply_directives(
        self,
        directives: Mapping[str, Directive],
        fragments: Iterable[Tuple[str, Fragment]],
    ) -> Tuple[ResourcePack, DataPack]:
        """Apply directives into a blank data pack and a blank resource pack."""
        assets, data = ResourcePack(), DataPack()

        for directive_name, fragment in fragments:
            directives[directive_name](fragment, assets, data)

        return assets, data

    def parse_fragments(
        self,
        source: str,
        directives: Mapping[str, Directive],
    ) -> Iterator[Tuple[str, Fragment]]:
        """Parse and yield pack fragments."""
        return iter([])


class TextExtractor(Extractor):
    """Extractor for plain text files."""

    def parse_fragments(
        self,
        source: str,
        directives: Mapping[str, Directive],
    ) -> Iterator[Tuple[str, Fragment]]:
        tokens = self.get_regex(directives).split(source + "\n")

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

    embedded_extractor: TextExtractor
    parser: MarkdownIt
    html_comment_regex: "re.Pattern[str]"

    def __init__(self):
        super().__init__()
        self.embedded_extractor = EmbeddedExtractor()
        self.parser = MarkdownIt()
        self.html_comment_regex = re.compile(r"<!--\s*(.+?)\s*-->")

    def extract(
        self,
        source: str,
        directives: Mapping[str, Directive],
        files: Optional[FileSystemPath] = None,
    ) -> Tuple[ResourcePack, DataPack]:
        return self.apply_directives(
            directives, self.parse_fragments(source, directives, files)
        )

    def parse_fragments(
        self,
        source: str,
        directives: Mapping[str, Directive],
        files: Optional[FileSystemPath] = None,
    ) -> Iterator[Tuple[str, Fragment]]:
        tokens = self.parser.parse(source)  # type: ignore
        regex = self.get_regex(directives)

        for i, token in enumerate(tokens):
            if (
                self.match_tokens(
                    tokens[i : i + 4],
                    "paragraph_open",
                    "inline",
                    "paragraph_close",
                    ["fence", "code_block"],
                )
                and (inline := tokens[i + 1])
                and inline.children
                and self.match_tokens(inline.children, "code_inline")
                and (match := regex.match(inline.children[0].content))
            ):
                directive, modifier, arguments = match.groups()
                yield directive, Fragment(
                    modifier, arguments.split(), tokens[i + 3].content
                )
            elif (
                self.match_tokens(
                    tokens[i : i + 2], "html_block", ["fence", "code_block"]
                )
                and (comment := self.html_comment_regex.match(token.content))
                and (match := regex.match(comment.group(1)))
            ):
                directive, modifier, arguments = match.groups()
                yield directive, Fragment(
                    modifier, arguments.split(), tokens[i + 1].content
                )
            elif token.type in ["fence", "code_block"]:
                yield from self.embedded_extractor.parse_fragments(
                    token.content, directives
                )

    def match_tokens(
        self, tokens: Optional[List[Token]], *token_types: Union[List[str], str]
    ) -> bool:
        """Return whether the list of tokens matches the provided token types."""
        return (
            tokens is not None
            and len(tokens) == len(token_types)
            and all(
                (
                    token_type == token.type
                    if isinstance(token_type, str)
                    else token.type in token_type
                )
                for token, token_type in zip(tokens, token_types)
            )
        )
