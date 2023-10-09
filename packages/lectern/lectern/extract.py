__all__ = [
    "Extractor",
    "TextExtractor",
    "EmbeddedExtractor",
    "MarkdownExtractor",
    "MarkdownParserWithUncheckedLinks",
    "FragmentLoader",
]


import json
import re
from dataclasses import replace
from itertools import islice
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    Set,
    Tuple,
    Union,
)
from urllib.parse import urlparse

from beet import Cache, DataPack, ResourcePack
from beet.core.utils import FileSystemPath
from markdown_it.main import MarkdownIt
from markdown_it.token import Token

from .directive import Directive
from .fragment import Fragment

FragmentLoader = Callable[[Fragment, Mapping[str, Directive]], Optional[Fragment]]


RELATIVE_PATH_REGEX = re.compile(r"^(?:assets|data)(?:/[a-zA-Z0-9_.]+)+$")


class Extractor:
    """Base class for extractors."""

    directives: Dict[str, Directive]
    regex: Optional["re.Pattern[str]"]
    escaped_regex: Optional["re.Pattern[str]"]
    cache: Optional[Cache]

    def __init__(self, cache: Optional[Cache] = None):
        self.directives = {}
        self.regex = None
        self.escaped_regex = None
        self.cache = cache

    def generate_directives(self) -> str:
        names = list(self.directives)
        names.append("overlay")
        names.append("endoverlay")
        return "|".join(names)

    def generate_regex(self) -> str:
        """Return a regex that can match the current directives."""
        names = self.generate_directives()
        modifier = r"(?:\((?P<modifier>[^)]*)\)|\b)"
        arguments = r"(?P<arguments>.*)"
        return f"@(?P<name>{names}){modifier}{arguments}"

    def generate_escaped_regex(self) -> str:
        """Return a regex that can match escaped fragments."""
        names = self.generate_directives()
        return rf"(@@+(?:{names})\b.*)"

    def compile_regex(self, regex: str) -> "re.Pattern[str]":
        """Return the compiled pattern for the directive regex."""
        return re.compile(f"^{regex}$", flags=re.MULTILINE)

    def get_regex(self, directives: Mapping[str, Directive]) -> "re.Pattern[str]":
        """Create and return the regex for the specified directives."""
        directives = dict(directives)

        if self.regex is None or self.directives != directives:
            self.directives = directives
            self.regex = self.compile_regex(self.generate_regex())
            self.escaped_regex = self.compile_regex(self.generate_escaped_regex())

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
        loaders: Iterable[FragmentLoader] = (),
    ) -> Tuple[ResourcePack, DataPack]:
        """Extract a resource pack and a data pack."""
        assets, data = ResourcePack(), DataPack()
        self.apply_directives(
            assets, data, directives, self.parse_fragments(source, directives), loaders
        )
        return assets, data

    def apply_directives(
        self,
        assets: ResourcePack,
        data: DataPack,
        directives: Mapping[str, Directive],
        fragments: Iterable[Fragment],
        loaders: Iterable[FragmentLoader] = (),
    ):
        """Apply directives into a blank data pack and a blank resource pack."""
        original_packs = assets, data
        added_overlays: Set[str] = set()

        for fragment in fragments:
            for loader in loaders:
                fragment = loader(fragment, directives)
                if not fragment:
                    break
            if fragment:
                if fragment.directive == "overlay":
                    directory = fragment.expect("directory")
                    formats: Any = (
                        json.loads(fragment.modifier) if fragment.modifier else None
                    )
                    assets = assets.overlays.setdefault(
                        directory, supported_formats=formats
                    )
                    data = data.overlays.setdefault(
                        directory, supported_formats=formats
                    )
                    added_overlays.add(directory)
                elif fragment.directive == "endoverlay":
                    assets, data = original_packs
                else:
                    directives[fragment.directive](fragment, assets, data)

        for pack in original_packs:
            for directory in added_overlays:
                if not pack.overlays[directory]:
                    del pack.overlays[directory]

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
        assert self.escaped_regex

        it = iter(tokens)
        newlines = next(it).count("\n")

        while True:
            try:
                directive, modifier, arguments, content = islice(it, 4)
            except ValueError:
                return
            else:
                content = content.partition("\n")[-1]
                content = "".join(
                    s.replace("@@", "@", 1) if i % 2 else s
                    for i, s in enumerate(self.escaped_regex.split(content))
                )
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

    def generate_escaped_regex(self) -> str:
        return r"(?://|#)\s*" + super().generate_escaped_regex()


class MarkdownParserWithUncheckedLinks(MarkdownIt):
    """MarkownIt subclass that removes link checks because lectern has its own logic."""

    def normalizeLink(self, url: str) -> str:
        return url

    def normalizeLinkText(self, link: str) -> str:
        return link

    def validateLink(self, url: str) -> bool:
        return True


class MarkdownExtractor(Extractor):
    """Extractor for markdown files."""

    text_extractor: TextExtractor
    embedded_extractor: TextExtractor
    comment_extractor: TextExtractor
    parser: MarkdownIt
    html_comment_regex: "re.Pattern[str]"
    embedded_sniffer: "re.Pattern[str]"

    def __init__(self, cache: Optional[Cache] = None):
        super().__init__(cache)
        self.text_extractor = TextExtractor(cache)
        self.embedded_extractor = EmbeddedExtractor(cache)
        self.comment_extractor = TextExtractor(cache)
        self.parser = MarkdownParserWithUncheckedLinks()
        self.html_comment_regex = re.compile(r"\s*<!--\s*(.+?)\s*-->\s*")
        self.embedded_sniffer = re.compile(
            r"^[ \t]*(?://|#)[ \t]*@[a-z0-9_]{3,}",
            re.MULTILINE,
        )

    def extract(
        self,
        source: str,
        directives: Mapping[str, Directive],
        loaders: Iterable[FragmentLoader] = (),
        external_files: Optional[FileSystemPath] = None,
    ) -> Tuple[ResourcePack, DataPack]:
        assets, data = ResourcePack(), DataPack()
        self.apply_directives(
            assets,
            data,
            directives,
            self.parse_fragments(source, directives, external_files),
            loaders,
        )
        return assets, data

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
                and (
                    match := regex.match(inline := inline.children[0].content)
                    or (
                        RELATIVE_PATH_REGEX.match(inline)
                        and (
                            directive := "@resource_pack"
                            if inline.startswith("assets")
                            else "@data_pack"
                        )
                        and regex.match(f"{directive} {inline}")
                    )
                )
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
                extractor = (
                    self.embedded_extractor
                    if self.embedded_sniffer.search(token.content)
                    else self.text_extractor
                )
                for fragment in extractor.parse_fragments(token.content, directives):
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
            and next((token.map[-1] for token in reversed(tokens) if token.map), 1)  # type: ignore
        )

    def create_link_fragment(
        self,
        start_line: int,
        end_line: int,
        match: "re.Match[str]",
        link: Any,
        external_files: Optional[FileSystemPath] = None,
    ) -> Fragment:
        """Helper for creating a fragment from a link."""
        url = str(link)
        path = None

        if urlparse(url).path == url:
            if external_files:
                path = Path(external_files, url).resolve()
            url = None

        return self.create_fragment(start_line, end_line, match, url=url, path=path)
