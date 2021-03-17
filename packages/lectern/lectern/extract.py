__all__ = [
    "Extractor",
    "TextExtractor",
    "EmbeddedExtractor",
    "MarkdownExtractor",
]


import re
from dataclasses import replace
from itertools import islice
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Mapping, Optional, Tuple, Union
from urllib.parse import unquote, urlparse

from beet import Cache, DataPack, ResourcePack
from beet.core.utils import FileSystemPath
from markdown_it import MarkdownIt
from markdown_it.common import normalize_url
from markdown_it.token import Token

from .directive import Directive
from .fragment import Fragment

# Patch markdown_it to allow arbitrary data urls
# https://github.com/executablebooks/markdown-it-py/issues/128
# TODO: Will soon be able to use custom validateLink
normalize_url.GOOD_DATA_RE = re.compile(r"^data:")


class Extractor:
    """Base class for extractors."""

    directives: Dict[str, Directive]
    regex: Optional["re.Pattern[str]"]
    cache: Optional[Cache]

    def __init__(self, cache: Optional[Cache] = None):
        self.directives = {}
        self.regex = None
        self.cache = cache

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

    def split(
        self,
        source: str,
        directives: Mapping[str, Directive],
    ) -> Iterator[Tuple[str, Optional[Fragment]]]:
        """Split the given content into fragments."""
        lines = source.splitlines(keepends=True)
        previous_line = 0

        for fragment in self.parse_fragments(source, directives):
            if fragment.start_line > previous_line:
                yield "".join(lines[previous_line : fragment.start_line]), None
            yield "".join(lines[fragment.start_line : fragment.end_line]), fragment
            previous_line = fragment.end_line

        if previous_line < len(lines):
            yield "".join(lines[previous_line:]), None

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
        fragments: Iterable[Fragment],
    ) -> Tuple[ResourcePack, DataPack]:
        """Apply directives into a blank data pack and a blank resource pack."""
        assets, data = ResourcePack(), DataPack()

        for fragment in fragments:
            directives[fragment.directive](fragment, assets, data)

        return assets, data

    def parse_fragments(
        self,
        source: str,
        directives: Mapping[str, Directive],
    ) -> Iterator[Fragment]:
        """Parse and yield pack fragments."""
        return iter([])

    def create_fragment(
        self,
        start_line: int,
        end_line: int,
        match: "re.Match[str]",
        content: Optional[str] = None,
        url: Optional[str] = None,
        path: Optional[FileSystemPath] = None,
    ):
        """Helper for creating a fragment from a matched pattern."""
        directive, modifier, arguments = match.groups()
        return Fragment(
            start_line=start_line,
            end_line=end_line,
            directive=directive,
            modifier=modifier,
            arguments=arguments.split(),
            content=content,
            url=url,
            path=path,
            cache=self.cache,
        )


class TextExtractor(Extractor):
    """Extractor for plain text files."""

    def parse_fragments(
        self,
        source: str,
        directives: Mapping[str, Directive],
    ) -> Iterator[Fragment]:
        tokens = self.get_regex(directives).split(source + "\n")

        it = iter(tokens)
        newlines = next(it).count("\n")

        while True:
            try:
                directive, modifier, arguments, content = islice(it, 4)
            except ValueError:
                return
            else:
                content = content.partition("\n")[-1]
                yield Fragment(
                    start_line=newlines,
                    end_line=(newlines := newlines + content.count("\n") + 1),
                    directive=directive,
                    modifier=modifier,
                    arguments=arguments.split(),
                    content=content[:-1] if content.endswith("\n") else content,
                    cache=self.cache,
                )


class EmbeddedExtractor(TextExtractor):
    """Extractor for directives embedded in markdown code blocks."""

    def generate_regex(self) -> str:
        return r"(?://|#)\s*" + super().generate_regex()


class MarkdownExtractor(Extractor):
    """Extractor for markdown files."""

    embedded_extractor: TextExtractor
    comment_extractor: TextExtractor
    parser: MarkdownIt
    html_comment_regex: "re.Pattern[str]"

    def __init__(self, cache: Optional[Cache] = None):
        super().__init__(cache)
        self.embedded_extractor = EmbeddedExtractor(cache)
        self.comment_extractor = TextExtractor(cache)
        self.parser = MarkdownIt()
        self.html_comment_regex = re.compile(r"\s*<!--\s*(.+?)\s*-->\s*")

    def extract(
        self,
        source: str,
        directives: Mapping[str, Directive],
        external_files: Optional[FileSystemPath] = None,
    ) -> Tuple[ResourcePack, DataPack]:
        return self.apply_directives(
            directives, self.parse_fragments(source, directives, external_files)
        )

    def parse_fragments(
        self,
        source: str,
        directives: Mapping[str, Directive],
        external_files: Optional[FileSystemPath] = None,
    ) -> Iterator[Fragment]:
        tokens = self.parser.parse(source)  # type: ignore
        regex = self.get_regex(directives)

        skip_to = 0

        for i, token in enumerate(tokens):
            if not token.map:
                continue

            current_line = token.map[0]
            if skip_to > current_line:
                continue

            #
            # `@directive args...`
            #
            # ```
            # content
            # ```
            #
            if (
                (
                    skip_to := self.match_tokens(
                        tokens[i : i + 4],
                        "paragraph_open",
                        "inline",
                        "paragraph_close",
                        ["fence", "code_block"],
                    )
                )
                and (inline := tokens[i + 1])
                and inline.children
                and self.match_tokens(inline.children, "code_inline")
                and (match := regex.match(inline.children[0].content))
            ):
                yield self.create_fragment(
                    current_line, skip_to, match, content=tokens[i + 3].content
                )

            #
            # `@directive args...`
            #
            # ![](path/to/image)
            #
            elif (
                (
                    skip_to := self.match_tokens(
                        tokens[i : i + 6],
                        "paragraph_open",
                        "inline",
                        "paragraph_close",
                        "paragraph_open",
                        "inline",
                        "paragraph_close",
                    )
                )
                and (inline := tokens[i + 1])
                and inline.children
                and self.match_tokens(inline.children, "code_inline")
                and (image := tokens[i + 4])
                and image.children
                and self.match_tokens(image.children, "image")
                and (link := image.children[0].attrGet("src"))
                and (match := regex.match(inline.children[0].content))
            ):
                yield self.create_link_fragment(
                    current_line, skip_to, match, link, external_files
                )

            #
            # `@directive args...`
            #
            # <details>
            #
            # ```
            # content
            # ```
            #
            # </details>
            #
            elif (
                (
                    skip_to := self.match_tokens(
                        tokens[i : i + 6],
                        "paragraph_open",
                        "inline",
                        "paragraph_close",
                        "html_block",
                        ["fence", "code_block"],
                        "html_block",
                    )
                )
                and (inline := tokens[i + 1])
                and inline.children
                and self.match_tokens(inline.children, "code_inline")
                and tokens[i + 3].content == "<details>\n"
                and tokens[i + 5].content == "</details>\n"
                and (match := regex.match(inline.children[0].content))
            ):
                yield self.create_fragment(
                    current_line, skip_to, match, content=tokens[i + 4].content
                )

            #
            # `@directive args...`
            #
            # <details>
            #
            # ![](path/to/image)
            #
            # </details>
            #
            elif (
                (
                    skip_to := self.match_tokens(
                        tokens[i : i + 8],
                        "paragraph_open",
                        "inline",
                        "paragraph_close",
                        "html_block",
                        "paragraph_open",
                        "inline",
                        "paragraph_close",
                        "html_block",
                    )
                )
                and (inline := tokens[i + 1])
                and inline.children
                and self.match_tokens(inline.children, "code_inline")
                and tokens[i + 3].content == "<details>\n"
                and tokens[i + 7].content == "</details>\n"
                and (image := tokens[i + 5])
                and image.children
                and self.match_tokens(image.children, "image")
                and (link := image.children[0].attrGet("src"))
                and (match := regex.match(inline.children[0].content))
            ):
                yield self.create_link_fragment(
                    current_line, skip_to, match, link, external_files
                )

            #
            # [`@directive args...`](path/to/content)
            #
            elif (
                (
                    skip_to := self.match_tokens(
                        tokens[i : i + 3],
                        "paragraph_open",
                        "inline",
                        "paragraph_close",
                    )
                )
                and (inline := tokens[i + 1])
                and inline.children
                and self.match_tokens(
                    inline.children,
                    "link_open",
                    "code_inline",
                    "link_close",
                )
                and (link := inline.children[0].attrGet("href"))
                and (match := regex.match(inline.children[1].content))
            ):
                yield self.create_link_fragment(
                    current_line, skip_to, match, link, external_files
                )

            #
            # <!-- @directive args... -->
            #
            # ```
            # content
            # ```
            #
            elif (
                (
                    skip_to := self.match_tokens(
                        tokens[i : i + 2],
                        "html_block",
                        ["fence", "code_block"],
                    )
                )
                and (comment := self.html_comment_regex.match(token.content))
                and (match := regex.match(comment.group(1)))
            ):
                yield self.create_fragment(
                    current_line, skip_to, match, content=tokens[i + 1].content
                )

            #
            # <!-- @directive args... -->
            #
            # ![](path/to/image)
            #
            elif (
                (
                    skip_to := self.match_tokens(
                        tokens[i : i + 4],
                        "html_block",
                        "paragraph_open",
                        "inline",
                        "paragraph_close",
                    )
                )
                and (comment := self.html_comment_regex.match(token.content))
                and (image := tokens[i + 2])
                and image.children
                and self.match_tokens(image.children, "image")
                and (link := image.children[0].attrGet("src"))
                and (match := regex.match(comment.group(1)))
            ):
                yield self.create_link_fragment(
                    current_line, skip_to, match, link, external_files
                )

            #
            # `@directive args...`
            #
            elif (
                (
                    skip_to := self.match_tokens(
                        tokens[i : i + 3],
                        "paragraph_open",
                        "inline",
                        "paragraph_close",
                    )
                )
                and (inline := tokens[i + 1])
                and inline.children
                and self.match_tokens(inline.children, "code_inline")
                and (match := regex.match(inline.children[0].content))
            ):
                yield self.create_fragment(current_line, skip_to, match)

            #
            # <!-- @directive args... -->
            #
            elif (
                token.type == "html_block"
                and (comment := self.html_comment_regex.match(token.content))
                and (match := regex.match(comment.group(1)))
            ):
                yield self.create_fragment(current_line, skip_to, match)

            #
            # ```
            # @directive args...
            #
            # content
            # ```
            #
            elif token.type in ["fence", "code_block"]:
                offset = int(token.type == "fence")
                for fragment in self.embedded_extractor.parse_fragments(
                    token.content,
                    directives,
                ):
                    yield replace(
                        fragment,
                        start_line=fragment.start_line + current_line + offset,
                        end_line=(skip_to := fragment.end_line + current_line),
                    )

            #
            # <!--
            # @directive args...
            #
            # content
            # -->
            #
            elif (
                token.type == "html_block"
                and (html := token.content.rstrip())
                and html.startswith("<!--")
                and html.endswith("-->")
            ):
                for fragment in self.comment_extractor.parse_fragments(
                    html[4:-3],
                    directives,
                ):
                    yield replace(
                        fragment,
                        start_line=fragment.start_line + current_line,
                        end_line=(skip_to := fragment.end_line + current_line),
                    )

    def match_tokens(
        self,
        tokens: Optional[List[Token]],
        *token_types: Union[List[str], str],
    ) -> int:
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
            and next((token.map[-1] for token in reversed(tokens) if token.map), 1)
        )

    def create_link_fragment(
        self,
        start_line: int,
        end_line: int,
        match: "re.Match[str]",
        link: str,
        external_files: Optional[FileSystemPath] = None,
    ) -> Fragment:
        """Helper for creating a fragment from a link."""
        url = unquote(link)  # TODO: Will soon be able to use custom normalizeLink
        path = None

        if urlparse(url).path == url:
            if external_files:
                path = Path(external_files, url).resolve()
            url = None

        return self.create_fragment(start_line, end_line, match, url=url, path=path)
