__all__ = [
    "Token",
    "TokenSpec",
    "TokenStream",
    "InvalidSyntax",
    "UnexpectedEOF",
    "UnexpectedToken",
]


import re
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Dict, Iterable, Iterator, List, NamedTuple, Optional, Tuple

from beet.core.utils import extra_field


class Token(NamedTuple):
    """Class representing a token."""

    type: str
    value: str
    pos: int
    lineno: int
    col_start: int
    col_end: int


class InvalidSyntax(Exception):
    """Raised when the parser encounters invalid syntax."""


class UnexpectedEOF(InvalidSyntax):
    """Raised when the parser reaches the end of the file unexpectedly."""

    expected_type: str
    expected_value: Optional[str]

    def __init__(
        self,
        expected_type: str,
        expected_value: Optional[str] = None,
    ) -> None:
        super().__init__(expected_type, expected_value)
        self.expected_type = expected_type
        self.expected_value = expected_value

    def __str__(self) -> str:
        value = "" if self.expected_value is None else " " + repr(self.expected_value)
        return f"Reached end of file instead of expected {self.expected_type}{value}"


class UnexpectedToken(InvalidSyntax):
    """Raised when the parser encounters an unexpected token."""

    token: Token
    expected_type: str
    expected_value: Optional[str]

    def __init__(
        self,
        token: Token,
        expected_type: str,
        expected_value: Optional[str] = None,
    ) -> None:
        super().__init__(token)
        self.token = token
        self.expected_type = expected_type
        self.expected_value = expected_value

    def __str__(self) -> str:
        value = "" if self.expected_value is None else " " + repr(self.expected_value)
        return f"Expected {self.expected_type}{value} but got {self.token.type} {self.token.value!r}"


@dataclass
class Checkpoint:
    """Allows committing the modifications."""

    committed: bool = False

    def commit(self):
        """Commit the checkpoint."""
        self.committed = True


TokenSpec = Tuple[Tuple[str, str], ...]


@dataclass
class TokenStream:
    """Stream for processing tokens extracted from an input string."""

    source: str
    token_spec: TokenSpec = ()

    pos: int = 0
    lineno: int = 1
    colno: int = 1

    index: int = -1
    tokens: List[Token] = extra_field(default_factory=list)
    indentation: List[int] = extra_field(default_factory=lambda: [0])

    regex: "re.Pattern[str]" = extra_field(init=False)
    regex_cache: Dict[TokenSpec, "re.Pattern[str]"] = extra_field(default_factory=dict)

    generator: Iterator[Token] = extra_field(init=False)

    def __post_init__(self):
        self.bake_regex()
        self.generator = self.tokenize()

    def bake_regex(self):
        """Turn the syntax in the `token_spec` attribute into a regex."""
        spec = self.token_spec + (
            ("comment", r"#.+$"),
            ("whitespace", r"\s+"),
        )
        self.regex = re.compile(
            "|".join(f"(?P<{name}>{regex})" for name, regex in spec), re.MULTILINE
        )

    @contextmanager
    def syntax(self, **kwargs: str) -> Iterator[None]:
        """Define token rules using regular expressions."""
        previous_spec = self.token_spec
        previous_tokens = self.tokens
        self.token_spec = tuple(kwargs.items())

        if self.index + 1 < len(previous_tokens):
            self.tokens = previous_tokens[: self.index + 1]

        if regex := self.regex_cache.get(self.token_spec):
            self.regex = regex
        else:
            self.bake_regex()
            self.regex_cache[self.token_spec] = self.regex

        try:
            yield
        finally:
            self.token_spec = previous_spec
            self.tokens = previous_tokens

    def filter(self, *token_types: str) -> Iterator[Token]:
        """Yield tokens matching the given types."""
        types = set(token_types)

        for token in self:
            if token.type in types:
                yield token

    def reject(self, *token_types: str, blanks: bool = False) -> Iterator[Token]:
        """Yield tokens expect those matching the given types."""
        types = set(token_types)

        if blanks:
            types |= {"whitespace", "newline", "indent", "dedent", "comment"}

        for token in self:
            if token.type not in types:
                yield token

    def skip(self, *token_types: str, blanks: bool = False) -> Optional[Token]:
        """Return the first token that doesn't match the given types."""
        types = set(token_types)

        if blanks:
            types |= {"whitespace", "newline", "indent", "dedent", "comment"}

        for token in self:
            if token.type not in types:
                return token

        return None

    @property
    def current(self) -> Token:
        """The current token."""
        return self.tokens[self.index]

    @property
    def previous(self) -> Token:
        """The previous token."""
        return self.tokens[self.index - 1]

    @property
    def rest(self) -> str:
        """The remaining input to parse."""
        return self.source[self.pos :]

    def head(self, characters: int = 50) -> str:
        """Return the next characters to parse."""
        return self.source[self.pos : self.pos + characters].partition("\n")[0]

    def emit(self, token_type: str, value: str = "") -> int:
        """Generate a token and return its index in the `tokens` list."""
        token = Token(
            token_type,
            value,
            self.pos,
            self.lineno,
            self.colno,
            self.colno + len(value),
        )

        self.pos += len(value)
        self.colno += len(value)
        self.tokens.append(token)

        return len(self.tokens) - 1

    def tokenize(self) -> Iterator[Token]:
        """Extract tokens from the input string."""
        while self.pos < len(self.source):
            if self.source[self.pos] == "\n":
                self.index = self.emit("newline", "\n")
                self.lineno += 1
                self.colno = 1
                yield self.current

            elif match := self.regex.match(self.source, self.pos):
                assert match.lastgroup

                if (
                    match.lastgroup != "comment"
                    and (
                        len(self.tokens) == 1
                        or len(self.tokens) > 1
                        and self.previous.type == "newline"
                    )
                    and self.current.type == "whitespace"
                ):
                    indent = len(self.current.value.expandtabs())

                    while indent < self.indentation[-1]:
                        self.index = self.emit("dedent")
                        self.indentation.pop()
                        yield self.current

                    if indent > self.indentation[-1]:
                        self.index = self.emit("indent")
                        self.indentation.append(indent)
                        yield self.current

                self.index = self.emit(match.lastgroup, match.group())
                yield self.current

            else:
                raise InvalidSyntax(self.head())

        while len(self.indentation) > 1:
            self.index = self.emit("dedent")
            self.indentation.pop()
            yield self.current

    def __iter__(self) -> "TokenStream":
        return self

    def __next__(self) -> Token:
        if self.index + 1 < len(self.tokens):
            self.index += 1
            return self.current
        return next(self.generator)

    @contextmanager
    def checkpoint(self) -> Iterator[Checkpoint]:
        """Reset the stream to the current token at the end of the with statement."""
        checkpoint = Checkpoint()
        previous_index = self.index

        try:
            yield checkpoint
        finally:
            if not checkpoint.committed:
                self.index = previous_index

    def peek(self, n: int = 1) -> Optional[Token]:
        """Return a token relative to the current index."""
        index = self.index + n

        if index < 0:
            return None
        if index < len(self.tokens):
            return self.tokens[index]

        with self.checkpoint():
            self.index = len(self.tokens) - 1

            for token in self:
                if self.index == index:
                    return token

    def expect(
        self,
        token_type: str,
        value: Optional[str] = None,
        skip: Iterable[str] = (),
        skip_blanks: bool = False,
    ) -> Token:
        """Check that the next token has a given type and value."""
        token = self.skip(*skip, blanks=skip_blanks)

        if not token:
            raise UnexpectedEOF(token_type, value)
        if token.type != token_type or value is not None and token.value != value:
            raise UnexpectedToken(token, token_type, value)

        return token

    def get(
        self,
        token_type: str,
        value: Optional[str] = None,
        skip: Iterable[str] = (),
        skip_blanks: bool = False,
    ) -> Optional[Token]:
        """Return the next token with the given type and value."""
        token = self.skip(*skip, blanks=skip_blanks)

        if (
            not token
            or token.type != token_type
            or value is not None
            and token.value != value
        ):
            return None

        return token
