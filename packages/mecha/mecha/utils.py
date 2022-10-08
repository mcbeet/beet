__all__ = [
    "QuoteHelper",
    "QuoteHelperWithUnicode",
    "JsonQuoteHelper",
    "InvalidEscapeSequence",
    "normalize_whitespace",
    "string_to_number",
    "number_to_string",
    "underline_code",
]


import re
from dataclasses import dataclass, field
from typing import Dict, Union

from tokenstream import InvalidSyntax, SourceLocation, Token, set_location

from .error import MechaError

ESCAPE_REGEX = re.compile(r"\\.")
UNICODE_ESCAPE_REGEX = re.compile(r"\\(?:u([0-9a-fA-F]{4})|.)")
AVOID_QUOTES_REGEX = re.compile(r"^[0-9A-Za-z_\.\+\-]+$")

WHITESPACE_REGEX = re.compile(r"\s+")

NOTABS_REGEX = re.compile(r"[^\t]")


def normalize_whitespace(op: str) -> str:
    """Replace whitespace with underscores."""
    return WHITESPACE_REGEX.sub("_", op).strip("_")


def string_to_number(string: str) -> Union[int, float]:
    """Helper for converting numbers to string and keeping their original type."""
    return float(string) if "." in string else int(string)


def number_to_string(number: Union[int, float]) -> str:
    """Helper for converting numbers to string and removing scientific notation."""
    value = str(number)
    if "e" in value:
        value = f"{number:.20f}".rstrip("0")
    return value


class InvalidEscapeSequence(MechaError):
    """Raised when a QuotedStringHandler encounters an invalid escape sequence."""

    characters: str
    index: int

    def __init__(self, characters: str, index: int):
        super().__init__(characters, index)
        self.characters = characters
        self.index = index


@dataclass
class QuoteHelper:
    """Helper for removing quotes and interpreting escape sequences."""

    escape_regex: "re.Pattern[str]" = ESCAPE_REGEX
    avoid_quotes_regex: "re.Pattern[str]" = AVOID_QUOTES_REGEX

    escape_sequences: Dict[str, str] = field(default_factory=dict)
    escape_characters: Dict[str, str] = field(init=False)

    def __post_init__(self):
        self.escape_characters = {v: k for k, v in self.escape_sequences.items()}

    def unquote_string(self, token: Token) -> str:
        """Remove quotes and substitute escaped characters."""
        if not token.value.startswith(('"', "'")):
            return token.value
        try:
            return self.escape_regex.sub(
                lambda match: self.handle_substitution(token, match),
                token.value[1:-1],
            )
        except InvalidEscapeSequence as exc:
            location = token.location.with_horizontal_offset(exc.index + 1)
            end_location = location.with_horizontal_offset(len(exc.characters))
            exc = InvalidSyntax(f"Invalid escape sequence {exc.characters}.")
            raise set_location(exc, location, end_location)

    def handle_substitution(self, token: Token, match: "re.Match[str]") -> str:
        """Handle escaped character sequence."""
        characters = match[0]

        if characters == "\\" + token.value[0]:
            return token.value[0]

        try:
            return self.escape_sequences[characters]
        except KeyError:
            raise InvalidEscapeSequence(characters, match.start()) from None

    def quote_string(self, value: str, quote: str = '"') -> str:
        """Wrap the string in quotes if it can't be represented unquoted."""
        if self.avoid_quotes_regex.match(value):
            return value
        for match, seq in self.escape_characters.items():
            value = value.replace(match, seq)
        return quote + value.replace(quote, "\\" + quote) + quote


@dataclass
class QuoteHelperWithUnicode(QuoteHelper):
    """Quote helper that handles unicode escape sequences."""

    escape_regex: "re.Pattern[str]" = UNICODE_ESCAPE_REGEX

    def handle_substitution(self, token: Token, match: "re.Match[str]") -> str:
        if unicode_hex := match[1]:
            return chr(int(unicode_hex, 16))
        return super().handle_substitution(token, match)


@dataclass
class JsonQuoteHelper(QuoteHelperWithUnicode):
    """Quote helper used for json."""

    escape_sequences: Dict[str, str] = field(
        default_factory=lambda: {
            r"\\": "\\",
            r"\f": "\f",
            r"\n": "\n",
            r"\r": "\r",
            r"\t": "\t",
        }
    )


def underline_code(
    source: str,
    location: SourceLocation,
    end_location: SourceLocation,
    padding: int = 1,
) -> str:
    """Underline code."""
    pos, lineno, colno = location
    end_pos, end_lineno, end_colno = end_location

    view_begin = pos
    view_end = end_pos

    for _ in range(padding + 1):
        try:
            view_begin = source.rindex("\n", 0, max(view_begin - 1, 0)) + 1
        except ValueError:
            view_begin = 0
        try:
            view_end = source.index("\n", min(view_end + 1, len(source)))
        except ValueError:
            view_end = len(source)

    view = source[view_begin:view_end].splitlines()
    view_start_line = lineno - source[view_begin:pos].count("\n")
    gutter = [f"{l + view_start_line} |" for l in range(len(view))]

    for line in reversed(range(lineno, end_lineno + 1)):
        index = line - view_start_line
        code = view[index] if index < len(view) else ""
        start = colno if line == lineno else 1
        stop = end_colno if line == end_lineno else len(code) + 1

        if start >= stop:
            stop = start + 1

        start = max(start, len(code) - len(code.lstrip()) + 1)
        stop = min(stop, len(code.rstrip()) + 1)

        if start < stop:
            underline = NOTABS_REGEX.sub(" ", code[: start - 1]) + "^" * (stop - start)
            view.insert(index + 1, underline)
            gutter.insert(index + 1, ":")

    gutter_size = max(max(len(g) for g in gutter), 8)
    return "\n".join(f"{g.rjust(gutter_size)}  {text}" for g, text in zip(gutter, view))
