__all__ = [
    "get_default_parsers",
    "get_stream_spec",
    "get_stream_scope",
    "get_stream_properties",
    "delegate",
    "parse_root",
    "parse_command",
    "parse_argument",
    "parse_bool",
    "NumericParser",
    "StringParser",
    "CoordinateParser",
    "Vector2Parser",
    "Vector3Parser",
    "INTEGER_PATTERN",
    "FLOAT_PATTERN",
]


import re
from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generic,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
)

from tokenstream import InvalidSyntax, SourceLocation, Token, TokenStream

from .ast import (
    AstChildren,
    AstCommand,
    AstCoordinate,
    AstNode,
    AstRoot,
    AstValue,
    AstVector2,
    AstVector3,
)
from .spec import CommandSpecification, Parser

NumericType = TypeVar("NumericType", float, int)


INTEGER_PATTERN: str = r"-?\d+"
FLOAT_PATTERN: str = r"-?(?:\d+\.?\d*|\.\d+)"


def get_default_parsers() -> Dict[str, Parser]:
    """Return the default parsers."""
    return {
        "root": parse_root,
        "command": parse_command,
        "argument": parse_argument,
        "brigadier:bool": parse_bool,
        "brigadier:double": NumericParser(
            type=float,
            name="double",
            pattern=FLOAT_PATTERN,
            min=-1.7976931348623157e308,
            max=1.7976931348623157e308,
        ),
        "brigadier:float": NumericParser(
            type=float,
            name="float",
            pattern=FLOAT_PATTERN,
            min=-3.4028234663852886e38,
            max=3.4028234663852886e38,
        ),
        "brigadier:integer": NumericParser(
            type=int,
            name="integer",
            pattern=INTEGER_PATTERN,
            min=-2147483648,
            max=2147483647,
        ),
        "brigadier:long": NumericParser(
            type=int,
            name="long",
            pattern=INTEGER_PATTERN,
            min=-9223372036854775808,
            max=9223372036854775807,
        ),
        "brigadier:string": StringParser(),
        "minecraft:angle": CoordinateParser(
            type=float,
            name="angle",
            min=-180.0,
            max=180.0,
            allow_local=False,
        ),
        "minecraft:block_pos": Vector3Parser(
            coordinate_parser=CoordinateParser(type=float),
        ),
    }


def get_stream_spec(stream: TokenStream) -> CommandSpecification:
    """Return the command specification associated with the token stream."""
    return stream.data["spec"]


def get_stream_scope(stream: TokenStream) -> Tuple[str, ...]:
    """Return the current scope associated with the token stream."""
    return stream.data.get("scope", ())


def get_stream_properties(stream: TokenStream) -> Dict[str, Any]:
    """Return the current command node properties associated with the token stream."""
    return stream.data.get("properties", {})


def delegate(stream: TokenStream, parser: str) -> Any:
    """Delegate parsing to a registered subparser."""
    spec = get_stream_spec(stream)

    if parser not in spec.parsers:
        raise ValueError(f"Unrecognized parser {parser!r}.")

    return spec.parsers[parser](stream)


def parse_root(stream: TokenStream) -> AstRoot:
    """Parse root."""
    with stream.syntax(comment=r"#.+$", literal=r"\S+"), stream.intercept("newline"):
        start = stream.peek()

        if not start:
            return AstRoot(
                filename=None,
                commands=AstChildren(),
                location=SourceLocation(0, 1, 1),
                end_location=SourceLocation(0, 1, 1),
            )

        commands: List[AstCommand] = []

        for _ in stream.peek_until():
            while stream.get("newline", "comment"):
                continue
            if stream.peek():
                commands.append(delegate(stream, "command"))

        return AstRoot(
            filename=None,
            commands=AstChildren(commands),
            location=start.location,
            end_location=stream.current.end_location,
        )


def parse_command(stream: TokenStream) -> AstCommand:
    """Parse command."""
    spec = get_stream_spec(stream)

    arguments: List[AstNode] = []
    scope: Tuple[str, ...] = ()

    with stream.checkpoint():
        location = stream.expect().location
        end_location = location

    while (tree := spec.flattened_tree[scope]) and not (
        tree.executable and stream.get("newline")
    ):
        literal_names = list(tree.get_literal_children())
        argument_names = list(tree.get_argument_children())

        with stream.alternative(bool(argument_names)):
            patterns = [("literal", name) for name in literal_names]
            token = stream.expect_any(*patterns)
            scope += (token.value,)
            if not TYPE_CHECKING:
                continue

        for name, alternative in stream.choose(*argument_names):
            with alternative, stream.provide(scope=scope + (name,)):
                arguments.append(delegate(stream, "argument"))
                scope += (name,)

        end_location = stream.current.end_location

    return AstCommand(
        identifier=":".join(scope),
        arguments=AstChildren(arguments),
        location=location,
        end_location=end_location,
    )


def parse_argument(stream: TokenStream) -> AstNode:
    """Parse argument."""
    spec = get_stream_spec(stream)
    scope = get_stream_scope(stream)

    tree = spec.flattened_tree[scope]

    if tree.parser:
        with stream.provide(properties=tree.properties or {}):
            return delegate(stream, tree.parser)

    raise ValueError(f"Missing argument parser in command tree {scope}.")


def parse_bool(stream: TokenStream) -> AstValue[bool]:
    """Parse brigadier bool."""
    token = stream.expect_any(("literal", "true"), ("literal", "false"))

    return AstValue[bool](
        value=token.value == "true",
        location=token.location,
        end_location=token.end_location,
    )


@dataclass
class NumericParser(Generic[NumericType]):
    """Parser for numeric values."""

    type: Type[NumericType]
    name: str
    pattern: str
    min: Optional[NumericType] = None
    max: Optional[NumericType] = None

    def __call__(self, stream: TokenStream) -> AstValue[NumericType]:
        properties = get_stream_properties(stream)

        with stream.syntax(**{self.name: self.pattern}):
            stream.expect(self.name)

        node = self.create_node(stream)

        minimum = properties.get("min", self.min)
        maximum = properties.get("max", self.max)

        if minimum is not None and node.value < minimum:
            raise stream.emit_error(
                InvalidSyntax(f"Expected value to be at least {minimum}.")
            )
        if maximum is not None and node.value > maximum:
            raise stream.emit_error(
                InvalidSyntax(f"Expected value to be at most {maximum}.")
            )

        return node

    def create_node(self, stream: TokenStream) -> AstValue[NumericType]:
        """Create the ast node."""
        token = stream.current
        value = self.type(token.value)

        return AstValue[NumericType](
            value=value,
            location=token.location,
            end_location=token.end_location,
        )


@dataclass
class StringParser:
    """Parser for string values."""

    type: str = "phrase"
    escape_regex: "re.Pattern[str]" = field(default_factory=lambda: re.compile(r"\\."))
    escape_sequences: Dict[str, str] = field(
        default_factory=lambda: {
            r"\n": "\n",
            r"\"": '"',
            r"\\": "\\",
        }
    )

    def __call__(self, stream: TokenStream) -> AstValue[str]:
        properties = get_stream_properties(stream)
        string_type = properties.get("type", self.type)

        if string_type == "greedy":
            with stream.syntax(line=r".+"):
                token = stream.expect("line")
        else:
            with stream.syntax(
                word=r"[0-9A-Za-z_\.\+\-]+",
                quoted_string=r'"(?:\\.|[^\\\n])*?"' "|" r"'(?:\\.|[^\\\n])*?'",
            ):
                if string_type == "word":
                    token = stream.expect("word")
                elif string_type == "phrase":
                    token = stream.expect_any("word", "quoted_string")
                else:
                    raise ValueError(f"Invalid string type {string_type!r}.")

        return AstValue[str](
            value=(
                self.unquote_string(token)
                if token.match("quoted_string")
                else token.value
            ),
            location=token.location,
            end_location=token.end_location,
        )

    def unquote_string(self, token: Token) -> str:
        """Remove quotes and substitute escaped characters."""
        return self.escape_regex.sub(
            lambda match: self.escape_sequences[match[0]], token.value[1:-1]
        )


@dataclass
class CoordinateParser(NumericParser[NumericType]):
    """Parser for coordinates."""

    name: str = "coordinate"
    pattern: str = r"[~^]?" + FLOAT_PATTERN + r"|[~^]"
    allow_absolute: bool = True
    allow_relative: bool = True
    allow_local: bool = True

    def __call__(self, stream: TokenStream) -> AstCoordinate[NumericType]:
        return super().__call__(stream)  # type: ignore

    def create_node(self, stream: TokenStream) -> AstCoordinate[NumericType]:
        token = stream.current

        if issubclass(self.type, int) and "." in token.value:
            raise stream.emit_error(InvalidSyntax(f"Decimal {self.name} not allowed."))

        value = token.value

        if token.value.startswith("~"):
            if not self.allow_relative:
                raise stream.emit_error(
                    InvalidSyntax(f"Relative {self.name} not allowed.")
                )
            prefix = "relative"
            value = value[1:]
        elif token.value.startswith("^"):
            if not self.allow_local:
                raise stream.emit_error(
                    InvalidSyntax(f"Local {self.name} not allowed.")
                )
            prefix = "local"
            value = value[1:]
        else:
            prefix = "absolute"

        return AstCoordinate[NumericType](
            prefix=prefix,
            value=self.type(value or "0"),
            location=token.location,
            end_location=token.end_location,
        )


@dataclass
class Vector2Parser(Generic[NumericType]):
    """Parser for vector2."""

    coordinate_parser: Parser

    def __call__(self, stream: TokenStream) -> AstVector2[NumericType]:
        x = self.coordinate_parser(stream)
        y = self.coordinate_parser(stream)

        return AstVector2[NumericType](
            x=x,
            y=y,
            location=x.location,
            end_location=y.end_location,
        )


@dataclass
class Vector3Parser(Generic[NumericType]):
    """Parser for vector3."""

    coordinate_parser: Parser

    def __call__(self, stream: TokenStream) -> AstVector3[NumericType]:
        x = self.coordinate_parser(stream)
        y = self.coordinate_parser(stream)
        z = self.coordinate_parser(stream)

        return AstVector3[NumericType](
            x=x,
            y=y,
            z=z,
            location=x.location,
            end_location=z.end_location,
        )
