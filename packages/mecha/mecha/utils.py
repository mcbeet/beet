__all__ = [
    "QuoteHelper",
    "string_to_number",
]


import re
from dataclasses import dataclass, field
from typing import Dict, Union

from tokenstream import InvalidSyntax, Token, set_location

from .error import InvalidEscapeSequence

ESCAPE_REGEX = re.compile(r"\\.")
AVOID_QUOTES_REGEX = re.compile(r"^[0-9A-Za-z_\.\+\-]+$")


def string_to_number(string: str) -> Union[int, float]:
    """Helper for converting numbers to string and keeping their original type."""
    return float(string) if "." in string else int(string)


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
            exc = InvalidSyntax(f"Invalid escape sequence {exc.characters!r}.")
            raise set_location(exc, location, end_location)

    def handle_substitution(self, token: Token, match: "re.Match[str]") -> str:
        """Handle escaped character sequence."""
        characters = match[0]

        if characters == "\\" + token.value[0]:
            return token.value[0]

        try:
            return self.escape_sequences[characters]
        except KeyError:
            raise InvalidEscapeSequence(characters, match.pos) from None

    def quote_string(self, value: str, quote: str = '"') -> str:
        """Wrap the string in quotes if it can't be represented unquoted."""
        if self.avoid_quotes_regex.match(value):
            return value
        for match, seq in self.escape_characters.items():
            value = value.replace(match, seq)
        return quote + value.replace(quote, "\\" + quote) + quote
