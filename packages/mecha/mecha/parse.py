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
    "JsonParser",
    "NbtParser",
    "parse_compound_tag",
    "parse_adjacent_nbt",
    "ResourceLocationParser",
    "BlockParser",
    "ItemParser",
    "LiteralStringParser",
    "RangeParser",
    "parse_objective",
    "parse_player_name",
    "parse_swizzle",
    "parse_team",
    "TimeParser",
    "parse_uuid",
    "SelectorParser",
    "parse_selector_scores",
    "parse_selector_advancements",
    "parse_entity",
    "parse_score_holder",
    "parse_message",
    "NbtPathParser",
    "INTEGER_PATTERN",
    "FLOAT_PATTERN",
    "CHAT_COLORS",
]


import re
from dataclasses import dataclass, field
from functools import partial
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generic,
    Iterator,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    overload,
)
from uuid import UUID

# pyright: reportMissingTypeStubs=false
from nbtlib import Byte, Double, Float, Int, Long, OutOfRange, Short, String
from tokenstream import InvalidSyntax, SourceLocation, Token, TokenStream

from .ast import (
    AstBlock,
    AstBlockState,
    AstChildren,
    AstCommand,
    AstCoordinate,
    AstItem,
    AstJson,
    AstJsonArray,
    AstJsonObject,
    AstJsonObjectEntry,
    AstJsonValue,
    AstMessage,
    AstNbt,
    AstNbtCompound,
    AstNbtCompoundEntry,
    AstNbtList,
    AstNbtPath,
    AstNbtPathSubscript,
    AstNbtValue,
    AstNode,
    AstRange,
    AstResourceLocation,
    AstRoot,
    AstSelector,
    AstSelectorAdvancementMatch,
    AstSelectorAdvancements,
    AstSelectorArgument,
    AstSelectorScoreMatch,
    AstSelectorScores,
    AstTime,
    AstValue,
    AstVector2,
    AstVector3,
)
from .error import InvalidEscapeSequence, UnrecognizedParser
from .spec import CommandSpecification, Parser

NumericType = TypeVar("NumericType", float, int)


INTEGER_PATTERN: str = r"-?\d+"
FLOAT_PATTERN: str = r"-?(?:\d+\.?\d*|\.\d+)"


CHAT_COLORS: List[str] = [
    "black",
    "dark_blue",
    "dark_green",
    "dark_aqua",
    "dark_red",
    "dark_purple",
    "gold",
    "gray",
    "dark_gray",
    "blue",
    "green",
    "aqua",
    "red",
    "light_purple",
    "yellow",
    "white",
]


# TODO: Move validation that doesn't break parsing into a separate pass
# TODO: Handle the extended syntax by default and validate vanilla compatibility in a separate pass


def get_default_parsers() -> Dict[str, Parser]:
    """Return the default parsers."""
    return {
        "root": parse_root,
        "command": parse_command,
        "argument": parse_argument,
        "json": JsonParser(),
        "nbt": NbtParser(),
        "selector": SelectorParser(),
        "selector:argument:x": delegate("brigadier:double"),
        "selector:argument:y": delegate("brigadier:double"),
        "selector:argument:z": delegate("brigadier:double"),
        "selector:argument:distance": delegate("minecraft:float_range"),
        "selector:argument:dx": delegate("brigadier:double"),
        "selector:argument:dy": delegate("brigadier:double"),
        "selector:argument:dz": delegate("brigadier:double"),
        "selector:argument:scores": parse_selector_scores,
        "selector:argument:tag": StringParser(type="word"),
        "selector:argument:team": StringParser(type="word"),
        "selector:argument:limit": delegate("brigadier:integer"),
        "selector:argument:sort": LiteralStringParser(
            [
                "nearest",
                "furthest",
                "random",
                "arbitrary",
            ],
        ),
        "selector:argument:level": delegate("minecraft:int_range"),
        "selector:argument:gamemode": LiteralStringParser(
            [
                "adventure",
                "creative",
                "spectator",
                "survival",
            ],
        ),
        "selector:argument:name": StringParser(type="phrase"),
        "selector:argument:x_rotation": delegate("minecraft:float_range"),
        "selector:argument:y_rotation": delegate("minecraft:float_range"),
        "selector:argument:type": ResourceLocationParser(),
        "selector:argument:nbt": delegate("minecraft:nbt_compound_tag"),
        "selector:argument:advancements": parse_selector_advancements,
        "selector:argument:predicate": delegate("minecraft:resource_location"),
        "brigadier:bool": parse_bool,
        "brigadier:double": NumericParser[float](
            type=float,
            name="double",
            pattern=FLOAT_PATTERN,
            min=-1.7976931348623157e308,
            max=1.7976931348623157e308,
        ),
        "brigadier:float": NumericParser[float](
            type=float,
            name="float",
            pattern=FLOAT_PATTERN,
            min=-3.4028234663852886e38,
            max=3.4028234663852886e38,
        ),
        "brigadier:integer": NumericParser[int](
            type=int,
            name="integer",
            pattern=INTEGER_PATTERN,
            min=-2147483648,
            max=2147483647,
        ),
        "brigadier:long": NumericParser[int](
            type=int,
            name="long",
            pattern=INTEGER_PATTERN,
            min=-9223372036854775808,
            max=9223372036854775807,
        ),
        "brigadier:string": StringParser(),
        "minecraft:angle": CoordinateParser[float](
            type=float,
            name="angle",
            min=-180.0,
            max=180.0,
            allow_local=False,
        ),
        "minecraft:block_pos": Vector3Parser[float](
            coordinate_parser=CoordinateParser[float](type=float),
        ),
        "minecraft:block_predicate": BlockParser(),
        "minecraft:block_state": BlockParser(
            resource_location_parser=ResourceLocationParser(allow_tag=False),
        ),
        "minecraft:color": LiteralStringParser(["reset"] + CHAT_COLORS),
        "minecraft:column_pos": Vector2Parser[int](
            coordinate_parser=CoordinateParser[int](
                type=int,
                allow_local=False,
            ),
        ),
        "minecraft:component": delegate("json"),
        "minecraft:dimension": delegate("minecraft:resource_location"),
        "minecraft:entity": parse_entity,
        "minecraft:entity_anchor": LiteralStringParser(["eyes", "feet"]),
        "minecraft:entity_summon": delegate("minecraft:resource_location"),
        "minecraft:float_range": RangeParser[float](type=float),
        "minecraft:function": ResourceLocationParser(),
        "minecraft:game_profile": delegate("minecraft:entity"),
        "minecraft:int_range": RangeParser[int](type=int),
        "minecraft:item_enchantment": StringParser(type="word"),
        "minecraft:item_predicate": ItemParser(),
        "minecraft:item_slot": StringParser(type="word"),
        "minecraft:item_stack": ItemParser(
            resource_location_parser=ResourceLocationParser(allow_tag=False),
        ),
        "minecraft:message": parse_message,
        "minecraft:mob_effect": delegate("minecraft:resource_location"),
        "minecraft:nbt_compound_tag": parse_compound_tag,
        "minecraft:nbt_path": NbtPathParser(),
        "minecraft:nbt_tag": delegate("nbt"),
        "minecraft:objective": parse_objective,
        "minecraft:objective_criteria": ResourceLocationParser(allow_tag=False),
        "minecraft:operation": LiteralStringParser(
            [
                "+=",
                "-=",
                "*=",
                "/=",
                "%=",
                "=",
                "<",
                ">",
                "><",
            ],
            r"\S+",
        ),
        # TODO: "minecraft:particle"
        "minecraft:resource_location": ResourceLocationParser(allow_tag=False),
        "minecraft:rotation": Vector2Parser[float](
            coordinate_parser=CoordinateParser[float](
                type=float,
                name="angle",
                min=-180.0,
                max=180.0,
                allow_local=False,
            )
        ),
        "minecraft:score_holder": parse_score_holder,
        "minecraft:scoreboard_slot": StringParser(type="word"),
        "minecraft:swizzle": parse_swizzle,
        "minecraft:team": parse_team,
        "minecraft:time": TimeParser(),
        "minecraft:uuid": parse_uuid,
        "minecraft:vec2": Vector2Parser(
            coordinate_parser=CoordinateParser[float](type=float),
        ),
        "minecraft:vec3": Vector3Parser(
            coordinate_parser=CoordinateParser[float](type=float),
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


@overload
def delegate(parser: str) -> Parser:
    ...


@overload
def delegate(parser: str, stream: TokenStream) -> Any:
    ...


def delegate(parser: str, stream: Optional[TokenStream] = None) -> Any:
    """Delegate parsing to a registered subparser."""
    if stream is None:
        return partial(delegate, parser)

    spec = get_stream_spec(stream)

    if parser not in spec.parsers:
        raise UnrecognizedParser(parser)

    return spec.parsers[parser](stream)


@dataclass
class QuotedStringHandler:
    """Class responsible for removing quotes and interpreting escape sequences."""

    escape_regex: "re.Pattern[str]" = field(default_factory=lambda: re.compile(r"\\."))
    escape_sequences: Dict[str, str] = field(default_factory=dict)

    def unquote_string(self, token: Token) -> str:
        """Remove quotes and substitute escaped characters."""
        try:
            return self.escape_regex.sub(
                lambda match: self.handle_substitution(token, match),
                token.value[1:-1],
            )
        except InvalidEscapeSequence as exc:
            location = token.location.with_horizontal_offset(exc.index + 1)
            raise (
                InvalidSyntax(
                    f"Invalid escape sequence {exc.characters!r}."
                ).set_location(
                    location,
                    location.with_horizontal_offset(len(exc.characters)),
                )
            )

    def handle_substitution(self, token: Token, match: "re.Match[str]") -> str:
        """Handle escaped character sequence."""
        characters = match[0]

        if characters == "\\" + token.value[0]:
            return token.value[0]

        try:
            return self.escape_sequences[characters]
        except KeyError:
            raise InvalidEscapeSequence(characters, match.pos) from None


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
                commands.append(delegate("command", stream))

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
                arguments.append(delegate("argument", stream))
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
            return delegate(tree.parser, stream)

    raise ValueError(f"Missing argument parser in command tree {scope}.")


def parse_bool(stream: TokenStream) -> AstValue[bool]:
    """Parse bool."""
    with stream.syntax(literal=r"\w+"):
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
            token = stream.expect(self.name)

        node = self.create_node(stream)

        minimum = properties.get("min", self.min)
        maximum = properties.get("max", self.max)

        if minimum is not None and node.value < minimum:
            raise token.emit_error(
                InvalidSyntax(f"Expected value to be at least {minimum}.")
            )
        if maximum is not None and node.value > maximum:
            raise token.emit_error(
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

    type: Optional[str] = None
    quoted_string_handler: QuotedStringHandler = field(
        default_factory=QuotedStringHandler
    )

    def __call__(self, stream: TokenStream) -> AstValue[str]:
        string_type = self.type or get_stream_properties(stream)["type"]

        if string_type == "greedy":
            with stream.intercept("whitespace"):
                while stream.get("whitespace"):
                    continue
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
                self.quoted_string_handler.unquote_string(token)
                if token.match("quoted_string")
                else token.value
            ),
            location=token.location,
            end_location=token.end_location,
        )


@dataclass
class CoordinateParser(NumericParser[NumericType]):
    """Parser for coordinates."""

    name: str = "coordinate"
    pattern: str = r"[~^]?" + FLOAT_PATTERN + r"|[~^]"
    allow_absolute: bool = True
    allow_relative: bool = True
    allow_local: bool = True

    def create_node(self, stream: TokenStream) -> AstCoordinate[NumericType]:  # type: ignore
        token = stream.current

        if issubclass(self.type, int) and "." in token.value:
            raise token.emit_error(InvalidSyntax(f"Decimal {self.name} not allowed."))

        value = token.value

        if token.value.startswith("~"):
            if not self.allow_relative:
                raise token.emit_error(
                    InvalidSyntax(f"Relative {self.name} not allowed.")
                )
            prefix = "relative"
            value = value[1:]
        elif token.value.startswith("^"):
            if not self.allow_local:
                raise token.emit_error(InvalidSyntax(f"Local {self.name} not allowed."))
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


@dataclass
class JsonParser:
    """Parser for json values."""

    quoted_string_handler: QuotedStringHandler = field(
        default_factory=lambda: QuotedStringHandler(
            escape_sequences={
                r"\\": "\\",
                r"\f": "\f",
                r"\n": "\n",
                r"\r": "\r",
                r"\t": "\t",
            }
        )
    )

    def __call__(self, stream: TokenStream) -> AstJson:
        with stream.syntax(
            curly=r"\{|\}",
            bracket=r"\[|\]",
            string=r'"(?:\\.|[^\\\n])*?"',
            number=r"-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?",
            colon=r":",
            comma=r",",
            literal=r"\w+",
        ):
            curly, bracket, string, number, null, true, false = stream.expect(
                ("curly", "{"),
                ("bracket", "["),
                "string",
                "number",
                ("literal", "null"),
                ("literal", "true"),
                ("literal", "false"),
            )

            if curly:
                entries: List[AstJsonObjectEntry] = []

                for key in stream.collect("string"):
                    stream.expect("colon")
                    value = self(stream)
                    entries.append(
                        AstJsonObjectEntry(
                            key=AstValue[str](
                                value=self.quoted_string_handler.unquote_string(key),
                                location=key.location,
                                end_location=key.end_location,
                            ),
                            value=value,
                            location=key.location,
                            end_location=value.end_location,
                        )
                    )

                    if not stream.get("comma"):
                        break

                close_curly = stream.expect(("curly", "}"))

                return AstJsonObject(
                    entries=AstChildren(entries),
                    location=curly.location,
                    end_location=close_curly.end_location,
                )

            elif bracket:
                elements: List[AstJson] = []

                close_bracket = stream.get(("bracket", "]"))

                if not close_bracket:
                    elements.append(self(stream))

                    for _ in stream.collect("comma"):
                        elements.append(self(stream))

                    close_bracket = stream.expect(("bracket", "]"))

                return AstJsonArray(
                    elements=AstChildren(elements),
                    location=bracket.location,
                    end_location=close_bracket.end_location,
                )

            if null:
                value = None
            elif true:
                value = True
            elif false:
                value = False
            elif string:
                value = self.quoted_string_handler.unquote_string(string)
            elif number:
                value = float(number.value)

            return AstJsonValue(
                value=value,  # type: ignore
                location=stream.current.location,
                end_location=stream.current.end_location,
            )


@dataclass
class NbtParser:
    """Parser for nbt tags."""

    number_suffixes: Dict[str, Type[Any]] = field(
        default_factory=lambda: {  # type: ignore
            "b": Byte,
            "s": Short,
            "l": Long,
            "f": Float,
            "d": Double,
        }
    )

    literal_aliases: Dict[str, Any] = field(
        default_factory=lambda: {  # type: ignore
            "true": Byte(1),
            "false": Byte(0),
        }
    )

    quoted_string_handler: QuotedStringHandler = field(
        default_factory=lambda: QuotedStringHandler(
            escape_sequences={
                r"\\": "\\",
            }
        )
    )

    def __call__(self, stream: TokenStream) -> AstNbt:
        with stream.syntax(
            curly=r"\{|\}",
            bracket=r"\[|\]",
            quoted_string=r'"(?:\\.|[^\\\n])*?"' "|" r"'(?:\\.|[^\\\n])*?'",
            number=r"[+-]?(?:[0-9]*?\.[0-9]+|[0-9]+\.[0-9]*?|[1-9][0-9]*|0)([eE][+-]?[0-9]+)?[bslfdBSLFD]?(?![a-zA-Z0-9._+-])",
            string=r"[a-zA-Z0-9._+-]+",
            colon=r":",
            comma=r",",
        ):
            curly, bracket, number, string, quoted_string = stream.expect(
                ("curly", "{"),
                ("bracket", "["),
                "number",
                "string",
                "quoted_string",
            )

            if curly:
                entries: List[AstNbtCompoundEntry] = []

                for key in stream.collect_any("number", "string", "quoted_string"):
                    stream.expect("colon")
                    value = self(stream)
                    entries.append(
                        AstNbtCompoundEntry(
                            key=AstValue[str](
                                value=(
                                    self.quoted_string_handler.unquote_string(key)
                                    if key.match("quoted_string")
                                    else key.value
                                ),
                                location=key.location,
                                end_location=key.end_location,
                            ),
                            value=value,
                            location=key.location,
                            end_location=value.end_location,
                        )
                    )

                    if not stream.get("comma"):
                        break

                close_curly = stream.expect(("curly", "}"))

                return AstNbtCompound(
                    entries=AstChildren(entries),
                    location=curly.location,
                    end_location=close_curly.end_location,
                )

            elif bracket:
                elements: List[AstNbt] = []

                for _ in stream.peek_until(("bracket", "]")):
                    elements.append(self(stream))

                    if not stream.get("comma"):
                        stream.expect(("bracket", "]"))
                        break

                for element in elements[1:]:
                    node_type = type(elements[0])
                    if (
                        type(element) != node_type
                        or isinstance(element, AstNbtValue)
                        and type(element.get_value()) != type(elements[0].get_value())
                    ):
                        raise InvalidSyntax(
                            "All the elements should have the same type."
                        ).set_location(
                            location=elements[0].location,
                            end_location=elements[-1].end_location,
                        )

                return AstNbtList(
                    elements=AstChildren(elements),
                    location=bracket.location,
                    end_location=stream.current.end_location,
                )

            if number:
                suffix = number.value[-1].lower()

                try:
                    if suffix in self.number_suffixes:
                        value = self.number_suffixes[suffix](number.value[:-1])
                    else:
                        value = (  # type: ignore
                            Double(number.value)
                            if "." in number.value
                            else Int(number.value)
                        )
                except (OutOfRange, ValueError):
                    value = String(number.value)  # type: ignore

            elif string:
                alias = string.value.lower()

                if alias in self.literal_aliases:
                    value = self.literal_aliases[alias]
                else:
                    value = String(string.value)  # type: ignore

            elif quoted_string:
                value = String(self.quoted_string_handler.unquote_string(quoted_string))  # type: ignore

            return AstNbtValue(
                value=value,  # type: ignore
                location=stream.current.location,
                end_location=stream.current.end_location,
            )


def parse_compound_tag(stream: TokenStream) -> AstNbtCompound:
    """Parse compound tag."""
    node = delegate("nbt", stream)

    if isinstance(node, AstNbtCompound):
        return node

    raise InvalidSyntax("Expected nbt compound tag.").set_location(
        location=node.location,
        end_location=node.end_location,
    )


def parse_adjacent_nbt(stream: TokenStream) -> Optional[AstNbtCompound]:
    """Parse adjacent nbt."""
    with stream.syntax(curly=r"\{|\}"), stream.intercept("whitespace"):
        found_curly = hint.match(("curly", "{")) if (hint := stream.peek()) else False
    return parse_compound_tag(stream) if found_curly else None


@dataclass
class ResourceLocationParser:
    """Parser for resource locations."""

    allow_tag: bool = True

    def __call__(self, stream: TokenStream) -> AstResourceLocation:
        with stream.syntax(resource_location=r"#?(?:[0-9a-z_\-\.]+:)?[0-9a-z_./-]+"):
            token = stream.expect("resource_location")
            value = token.value
            location = token.location

            if is_tag := value.startswith("#"):
                if not self.allow_tag:
                    raise token.emit_error(
                        InvalidSyntax(f"Reference to tag {token.value!r} not allowed.")
                    )
                value = value[1:]
                location = location.with_horizontal_offset(1)

            namespace, _, path = value.rpartition(":")

            if namespace:
                namespace = AstValue[str](
                    value=namespace,
                    location=location,
                    end_location=location.with_horizontal_offset(len(namespace)),
                )
                location = namespace.end_location.with_horizontal_offset(1)
            else:
                namespace = None

            return AstResourceLocation(
                is_tag=is_tag,
                namespace=namespace,
                path=AstValue[str](
                    value=path, location=location, end_location=token.end_location
                ),
                location=token.location,
                end_location=token.end_location,
            )


@dataclass
class BlockParser:
    """Parser for minecraft blocks."""

    resource_location_parser: Parser = field(default_factory=ResourceLocationParser)

    allow_block_states: bool = True
    allow_data_tags: bool = True

    def __call__(self, stream: TokenStream) -> AstBlock:
        identifier = self.resource_location_parser(stream)
        location = identifier.location
        end_location = identifier.end_location

        with stream.syntax(
            bracket=r"\[|\]",
            state=r"[a-z0-9_]+",
            equal=r"=",
            comma=r",",
        ), stream.checkpoint() as commit:
            block_states: List[AstBlockState] = []

            with stream.intercept("whitespace"):
                stream.expect(("bracket", "["))

            commit()

            for name in stream.collect("state"):
                stream.expect("equal")
                value = stream.expect("state")

                block_states.append(
                    AstBlockState(
                        key=AstValue[str](
                            value=name.value,
                            location=name.location,
                            end_location=name.end_location,
                        ),
                        value=AstValue[str](
                            value=value.value,
                            location=value.location,
                            end_location=value.end_location,
                        ),
                        location=name.location,
                        end_location=value.end_location,
                    )
                )

                if not stream.get("comma"):
                    break

            close_bracket = stream.expect(("bracket", "]"))
            end_location = close_bracket.end_location

        data_tags = parse_adjacent_nbt(stream)

        if block_states and not self.allow_block_states:
            raise InvalidSyntax("Block states not allowed.").set_location(
                location=block_states[0].location,
                end_location=block_states[-1].end_location,
            )

        if data_tags is not None and not self.allow_data_tags:
            raise InvalidSyntax("Data tags not allowed.").set_location(
                location=data_tags.location,
                end_location=data_tags.end_location,
            )

        return AstBlock(
            identifier=identifier,
            block_states=AstChildren(block_states),
            data_tags=data_tags,
            location=location,
            end_location=(
                data_tags.end_location if data_tags is not None else end_location
            ),
        )


@dataclass
class ItemParser:
    """Parser for minecraft items."""

    resource_location_parser: Parser = field(default_factory=ResourceLocationParser)

    allow_data_tags: bool = True

    def __call__(self, stream: TokenStream) -> AstItem:
        identifier = self.resource_location_parser(stream)
        location = identifier.location
        end_location = identifier.end_location

        data_tags = parse_adjacent_nbt(stream)

        if data_tags is not None and not self.allow_data_tags:
            raise InvalidSyntax("Data tags not allowed.").set_location(
                location=data_tags.location,
                end_location=data_tags.end_location,
            )

        return AstItem(
            identifier=identifier,
            data_tags=data_tags,
            location=location,
            end_location=(
                data_tags.end_location if data_tags is not None else end_location
            ),
        )


@dataclass
class LiteralStringParser:
    """Parser for literal strings."""

    values: List[str]
    pattern: str = r"\w+"

    def __call__(self, stream: TokenStream) -> AstValue[str]:
        with stream.syntax(literal=self.pattern):
            patterns = [("literal", value) for value in self.values]
            token = stream.expect_any(*patterns)

        return AstValue[str](
            value=token.value,
            location=token.location,
            end_location=token.end_location,
        )


@dataclass
class RangeParser(Generic[NumericType]):
    """Parser for ranges."""

    type: Type[NumericType]
    pattern: str = (
        fr"\.\.{FLOAT_PATTERN}|{FLOAT_PATTERN}\.\.(?:{FLOAT_PATTERN})?|{FLOAT_PATTERN}"
    )

    def __call__(self, stream: TokenStream) -> AstRange[NumericType]:
        with stream.syntax(range=self.pattern):
            token = stream.expect("range")
            minimum, separator, maximum = token.value.partition("..")

            if not separator:
                maximum = minimum

            if issubclass(self.type, int) and "." in minimum:
                raise token.emit_error(InvalidSyntax(f"Decimal minimum not allowed."))
            if issubclass(self.type, int) and "." in maximum:
                raise token.emit_error(InvalidSyntax(f"Decimal maximum not allowed."))

            return AstRange[NumericType](
                min=self.type(minimum) if minimum else None,
                max=self.type(maximum) if maximum else None,
                location=token.location,
                end_location=token.end_location,
            )


def parse_objective(stream: TokenStream) -> AstValue[str]:
    """Parse objective."""
    with stream.syntax(objective=r"[a-zA-Z0-9_.+-]+|\*"):
        token = stream.expect("objective")

        if len(token.value) > 16:
            raise token.emit_error(
                InvalidSyntax("Objective name must be limited to 16 characters.")
            )

        return AstValue[str](
            value=token.value,
            location=token.location,
            end_location=token.end_location,
        )


def parse_player_name(stream: TokenStream) -> AstValue[str]:
    """Parse player name."""
    with stream.syntax(name=r"[a-zA-Z0-9_.+-]+"):
        token = stream.expect("name")

        if len(token.value) > 16:
            raise token.emit_error(
                InvalidSyntax("Player name must be limited to 16 characters.")
            )

        return AstValue[str](
            value=token.value,
            location=token.location,
            end_location=token.end_location,
        )


def parse_swizzle(stream: TokenStream) -> AstValue[str]:
    """Parse swizzle."""
    with stream.syntax(literal=r"\w+"):
        token = stream.expect("literal")

    if not 1 <= len(token.value) <= 3 or len(set(token.value)) < len(token.value):
        raise token.emit_error(InvalidSyntax(f"Invalid swizzle {token.value!r}."))

    return AstValue[str](
        value=token.value,
        location=token.location,
        end_location=token.end_location,
    )


def parse_team(stream: TokenStream) -> AstValue[str]:
    """Parse team."""
    with stream.syntax(team=r"[a-zA-Z0-9_.+-]+"):
        token = stream.expect("team")

        return AstValue[str](
            value=token.value,
            location=token.location,
            end_location=token.end_location,
        )


@dataclass
class TimeParser(NumericParser[float]):
    """Parser for time."""

    type: Type[float] = float
    name: str = "time"
    pattern: str = FLOAT_PATTERN + r"[dst]?"

    def create_node(self, stream: TokenStream) -> AstTime:  # type: ignore
        """Create the ast node."""
        token = stream.current
        value = token.value

        if value.endswith(("d", "s", "t")):
            suffix = value[-1]
            value = value[:-1]
        else:
            suffix = None

        return AstTime(
            value=self.type(value),
            suffix=suffix,  # type: ignore
            location=token.location,
            end_location=token.end_location,
        )


def parse_uuid(stream: TokenStream) -> AstValue[UUID]:
    """Parse uuid."""
    with stream.syntax(uuid="-".join([r"[a-fA-F0-9]+"] * 5)):
        token = stream.expect("uuid")

        return AstValue[UUID](
            value=UUID(token.value),
            location=token.location,
            end_location=token.end_location,
        )


@dataclass
class SelectorParser:
    """Parser for selectors."""

    amount: str = "multiple"

    def __call__(self, stream: TokenStream) -> AstSelector:
        properties = get_stream_properties(stream)

        with stream.syntax(
            selector=r"@[praes]\[?",
            bracket=r"\[|\]",
            argument=r"[a-z_]+",
            equal=r"=",
            comma=r",",
            exclamation=r"!",
        ):
            token = stream.expect("selector")
            variable = token.value[1]
            location = token.location
            end_location = token.end_location

            is_single = variable in "prs"

            arguments: List[AstSelectorArgument] = []

            if token.value.endswith("["):
                for key in stream.collect("argument"):
                    stream.expect("equal")

                    inverted = stream.get("exclamation") is not None

                    try:
                        value = delegate(f"selector:argument:{key.value}", stream)
                    except UnrecognizedParser as exc:
                        if not exc.parser.startswith("selector:argument:"):
                            raise
                        raise key.emit_error(
                            InvalidSyntax(f"Invalid selector argument {key.value!r}.")
                        ) from exc

                    arguments.append(
                        AstSelectorArgument(
                            inverted=inverted,
                            key=AstValue[str](
                                value=key.value,
                                location=key.location,
                                end_location=key.end_location,
                            ),
                            value=value,
                            location=key.location,
                            end_location=value.end_location,
                        )
                    )

                    if key.value == "limit":
                        is_single = value.value == 1

                    if not stream.get("comma"):
                        break

                close_bracket = stream.expect(("bracket", "]"))
                end_location = close_bracket.end_location

        amount = properties.get("amount", self.amount)

        if amount not in ["single", "multiple"]:
            raise ValueError(f"Invalid selector amount {amount!r}.")

        if amount == "single" and not is_single:
            raise InvalidSyntax(f"Multiple entities not allowed.").set_location(
                location=location,
                end_location=end_location,
            )

        return AstSelector(
            variable=variable,  # type: ignore
            arguments=AstChildren(arguments),
            location=location,
            end_location=end_location,
        )


def parse_selector_scores(stream: TokenStream) -> AstSelectorScores:
    """Parse selector scores."""
    with stream.syntax(
        curly=r"\{|\}",
        objective=r"[a-zA-Z0-9_.+-]+",
        equal=r"=",
        comma=r",",
    ):
        curly = stream.expect(("curly", "{"))

        scores: List[AstSelectorScoreMatch] = []

        for objective in stream.collect("objective"):
            stream.expect("equal")
            value = delegate("minecraft:integer_range", stream)

            scores.append(
                AstSelectorScoreMatch(
                    objective=AstValue[str](
                        value=objective.value,
                        location=objective.location,
                        end_location=objective.end_location,
                    ),
                    value=value,
                    location=objective.location,
                    end_location=value.end_location,
                )
            )

            if not stream.get("comma"):
                break

        close_curly = stream.expect(("curly", "}"))

        return AstSelectorScores(
            scores=AstChildren(scores),
            location=curly.location,
            end_location=close_curly.end_location,
        )


def parse_selector_advancements(stream: TokenStream) -> AstSelectorAdvancements:
    """Parse selector advancements."""
    with stream.syntax(curly=r"\{|\}", equal=r"=", comma=r","):
        curly = stream.expect(("curly", "{"))

        advancements: List[AstSelectorAdvancementMatch] = []

        for _ in stream.peek_until(("curly", "}")):
            name = delegate("minecraft:resource_location", stream)
            stream.expect("equal")
            value = delegate("brigadier:bool", stream)

            advancements.append(
                AstSelectorAdvancementMatch(
                    name=name,
                    value=value,
                    location=name.location,
                    end_location=value.end_location,
                )
            )

            if not stream.get("comma"):
                stream.expect(("curly", "}"))
                break

        return AstSelectorAdvancements(
            advancements=AstChildren(advancements),
            location=curly.location,
            end_location=stream.current.end_location,
        )


def parse_entity(stream: TokenStream) -> Any:
    """Parse entity."""
    hint = stream.peek()

    if hint:
        if hint.value.startswith("@"):
            return delegate("selector", stream)

        if hint.value.count("-") == 4:
            with stream.alternative():
                return delegate("minecraft:uuid", stream)

    return parse_player_name(stream)


def parse_score_holder(stream: TokenStream) -> Any:
    """Parse score holder."""
    with stream.syntax(wildcard=r"\*"):
        if token := stream.get("wildcard"):
            return AstValue[str](
                value=token.value,
                location=token.location,
                end_location=token.end_location,
            )
    return delegate("minecraft:entity", stream)


def parse_message(stream: TokenStream) -> AstMessage:
    """Parse message."""
    with stream.intercept("whitespace"):
        while stream.get("whitespace"):
            continue

    with stream.syntax(selector=r"@[praes]"):
        sentence: List[Any] = []

        for selector, literal in stream.collect("selector", "literal"):
            if selector:
                stream.index -= 1
                sentence.append(delegate("selector", stream))
            elif literal:
                sentence.append(
                    AstValue[str](
                        value=literal.value,
                        location=literal.location,
                        end_location=literal.end_location,
                    )
                )

    if not sentence:
        raise stream.emit_error(InvalidSyntax("Empty message not allowed."))

    return AstMessage(
        sentence=AstChildren(sentence),
        location=sentence[0].location,
        end_location=sentence[-1].end_location,
    )


@dataclass
class NbtPathParser:
    quoted_string_handler: QuotedStringHandler = field(
        default_factory=lambda: QuotedStringHandler(
            escape_sequences={
                r"\\": "\\",
            }
        )
    )

    def __call__(self, stream: TokenStream) -> AstNbtPath:
        nodes: List[Any] = []

        with stream.syntax(
            dot=r"\.",
            curly=r"\{|\}",
            bracket=r"\[|\]",
            quoted_string=r'"(?:\\.|[^\\\n])*?"' "|" r"'(?:\\.|[^\\\n])*?'",
            string=r"[a-zA-Z0-9_+-]+",
        ):
            nodes.extend(self.parse_modifiers(stream))

            while not nodes or stream.get("dot"):
                quoted_string, string = stream.expect("quoted_string", "string")

                if quoted_string:
                    nodes.append(
                        AstValue[str](
                            value=self.quoted_string_handler.unquote_string(
                                quoted_string
                            ),
                            location=quoted_string.location,
                            end_location=quoted_string.end_location,
                        )
                    )
                elif string:
                    nodes.append(
                        AstValue[str](
                            value=string.value,
                            location=string.location,
                            end_location=string.end_location,
                        )
                    )

                nodes.extend(self.parse_modifiers(stream))

        if not nodes:
            raise stream.emit_error(InvalidSyntax("Empty nbt path not allowed."))

        return AstNbtPath(
            nodes=AstChildren(nodes),
            location=nodes[0].location,
            end_location=nodes[-1].end_location,
        )

    def parse_modifiers(self, stream: TokenStream) -> Iterator[Any]:
        """Parse named tag modifiers."""
        hint = stream.peek()

        if hint and hint.match(("curly", "{")):
            yield delegate("minecraft:nbt_compound_tag", stream)
            return

        while bracket := stream.get(("bracket", "[")):
            match = None

            hint = stream.peek()
            if hint and hint.match(("curly", "{")):
                match = delegate("minecraft:nbt_compound_tag", stream)
            elif hint and not hint.match(("bracket", "]")):
                match = delegate("brigadier:integer", stream)

            close_bracket = stream.expect(("bracket", "]"))

            yield AstNbtPathSubscript(
                match=match,
                location=bracket.location,
                end_location=close_bracket.end_location,
            )
