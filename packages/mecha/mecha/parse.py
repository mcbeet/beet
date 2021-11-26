__all__ = [
    "get_default_parsers",
    "get_parsers",
    "get_stream_spec",
    "get_stream_scope",
    "get_stream_properties",
    "get_stream_multiline",
    "get_stream_line_indentation",
    "UnrecognizedParser",
    "delegate",
    "consume_line_continuation",
    "parse_root",
    "parse_command",
    "parse_argument",
    "MultilineParser",
    "parse_bool",
    "NumericParser",
    "CoordinateParser",
    "IntegerConstraint",
    "MinMaxConstraint",
    "RestrictCoordinateConstraint",
    "StringParser",
    "parse_string_argument",
    "Vector2Parser",
    "Vector3Parser",
    "JsonParser",
    "TypeConstraint",
    "NbtParser",
    "AdjacentConstraint",
    "ResourceLocationParser",
    "NoTagConstraint",
    "BlockParser",
    "parse_block_states",
    "ItemParser",
    "NoBlockStatesConstraint",
    "NoDataTagsConstraint",
    "LiteralParser",
    "LiteralConstraint",
    "RangeParser",
    "IntegerRangeConstraint",
    "LengthConstraint",
    "CommentDisambiguation",
    "parse_swizzle",
    "TimeParser",
    "parse_uuid",
    "SelectorParser",
    "SelectorArgumentParser",
    "SelectorArgumentInvertConstraint",
    "SelectorArgumentNoValueConstraint",
    "parse_selector_scores",
    "parse_selector_advancements",
    "SelectorPlayerConstraint",
    "SelectorTypeConstraint",
    "SelectorSingleConstraint",
    "SelectorAmountConstraint",
    "EntityParser",
    "ScoreHolderParser",
    "parse_message",
    "NbtPathParser",
    "parse_particle",
    "AggregateParser",
    "SingleLineConstraint",
    "ResetSyntaxParser",
    "NUMBER_PATTERN",
]


from contextlib import nullcontext
from dataclasses import dataclass, field
from functools import partial
from typing import (
    Any,
    Dict,
    Iterator,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
    Union,
    overload,
)
from uuid import UUID

# pyright: reportMissingTypeStubs=false
from nbtlib import Byte, Double, Float, Int, Long, OutOfRange, Short, String
from tokenstream import InvalidSyntax, SourceLocation, TokenStream, set_location

from .ast import (
    AstBlock,
    AstBlockParticleParameters,
    AstBlockState,
    AstBool,
    AstChildren,
    AstCommand,
    AstCoordinate,
    AstDustColorTransitionParticleParameters,
    AstDustParticleParameters,
    AstFallingDustParticleParameters,
    AstItem,
    AstItemParticleParameters,
    AstJson,
    AstJsonArray,
    AstJsonObject,
    AstJsonObjectEntry,
    AstJsonObjectKey,
    AstJsonValue,
    AstLiteral,
    AstMessage,
    AstNbt,
    AstNbtByteArray,
    AstNbtCompound,
    AstNbtCompoundEntry,
    AstNbtCompoundKey,
    AstNbtIntArray,
    AstNbtList,
    AstNbtLongArray,
    AstNbtPath,
    AstNbtPathSubscript,
    AstNbtValue,
    AstNode,
    AstNumber,
    AstParticle,
    AstRange,
    AstResourceLocation,
    AstRoot,
    AstSelector,
    AstSelectorAdvancementMatch,
    AstSelectorAdvancementPredicateMatch,
    AstSelectorAdvancements,
    AstSelectorArgument,
    AstSelectorScoreMatch,
    AstSelectorScores,
    AstString,
    AstTime,
    AstUUID,
    AstVector2,
    AstVector3,
    AstVibrationParticleParameters,
)
from .error import MechaError
from .spec import CommandSpec, Parser
from .utils import (
    QuoteHelper,
    QuoteHelperWithUnicode,
    VersionNumber,
    split_version,
    string_to_number,
)

NUMBER_PATTERN: str = r"-?(?:\d+\.?\d*|\.\d+)"


def get_default_parsers() -> Dict[str, Parser]:
    """Return the default parsers."""
    return {
        ################################################################################
        # Primitives
        ################################################################################
        "literal": LiteralParser(name="literal"),
        "bool": parse_bool,
        "numeric": NumericParser(),
        "integer": IntegerConstraint(delegate("numeric")),
        "coordinate": CoordinateParser(),
        "integer_coordinate": IntegerConstraint(delegate("coordinate")),
        "time": TimeParser(),
        "word": StringParser(type="word"),
        "phrase": StringParser(type="phrase"),
        "greedy": StringParser(type="greedy"),
        "json": MultilineParser(JsonParser()),
        "json_object": TypeConstraint(
            parser=delegate("json"),
            type=AstJsonObject,
            message="Expected json object.",
        ),
        "nbt": MultilineParser(NbtParser()),
        "nbt_compound": TypeConstraint(
            parser=delegate("nbt"),
            type=AstNbtCompound,
            message="Expected nbt compound.",
        ),
        "adjacent_nbt_compound": AdjacentConstraint(
            parser=delegate("nbt_compound"),
            hint=r"\{",
        ),
        "nbt_path": NbtPathParser(),
        "range": RangeParser(),
        "integer_range": IntegerRangeConstraint(delegate("range")),
        "resource_location_or_tag": CommentDisambiguation(ResourceLocationParser()),
        "resource_location": NoTagConstraint(delegate("resource_location_or_tag")),
        "uuid": parse_uuid,
        "objective": LiteralParser("objective", r"[a-zA-Z0-9_.+-]+|\*"),
        "player_name": CommentDisambiguation(delegate("literal")),
        "swizzle": parse_swizzle,
        "team": LiteralParser("team", r"[a-zA-Z0-9_.+-]+"),
        "block_predicate": BlockParser(
            resource_location_parser=delegate("resource_location_or_tag"),
            block_states_parser=AdjacentConstraint(
                parser=MultilineParser(parse_block_states),
                hint=r"\[",
            ),
        ),
        "block_state": BlockParser(
            resource_location_parser=delegate("resource_location"),
            block_states_parser=AdjacentConstraint(
                parser=MultilineParser(parse_block_states),
                hint=r"\[",
            ),
        ),
        "item_predicate": ItemParser(
            resource_location_parser=delegate("resource_location_or_tag"),
        ),
        "item_stack": ItemParser(
            resource_location_parser=delegate("resource_location"),
        ),
        ################################################################################
        # Particle
        ################################################################################
        "particle": parse_particle,
        "particle:minecraft:dust": AggregateParser(
            type=AstDustParticleParameters,
            fields={
                "red": delegate("numeric"),
                "green": delegate("numeric"),
                "blue": delegate("numeric"),
                "size": delegate("numeric"),
            },
        ),
        "particle:minecraft:dust_color_transition": AggregateParser(
            type=AstDustColorTransitionParticleParameters,
            fields={
                "red": delegate("numeric"),
                "green": delegate("numeric"),
                "blue": delegate("numeric"),
                "size": delegate("numeric"),
                "end_red": delegate("numeric"),
                "end_green": delegate("numeric"),
                "end_blue": delegate("numeric"),
            },
        ),
        "particle:minecraft:block": AggregateParser(
            type=AstBlockParticleParameters,
            fields={"block": delegate("block_state")},
        ),
        "particle:minecraft:falling_dust": AggregateParser(
            type=AstFallingDustParticleParameters,
            fields={"block": delegate("block_state")},
        ),
        "particle:minecraft:item": AggregateParser(
            type=AstItemParticleParameters,
            fields={"item": delegate("item_stack")},
        ),
        "particle:minecraft:vibration": AggregateParser(
            type=AstVibrationParticleParameters,
            fields={
                "x1": delegate("numeric"),
                "y1": delegate("numeric"),
                "z1": delegate("numeric"),
                "x2": delegate("numeric"),
                "y2": delegate("numeric"),
                "z2": delegate("numeric"),
                "duration": delegate("integer"),
            },
        ),
        ################################################################################
        # Selector
        ################################################################################
        "selector": MultilineParser(SelectorParser()),
        "selector:argument": SelectorArgumentInvertConstraint(
            SelectorArgumentNoValueConstraint(
                SelectorArgumentParser(),
                allow_no_value=["tag", "team"],
            ),
            allow_invert=[
                "tag",
                "team",
                "gamemode",
                "name",
                "type",
                "nbt",
                "predicate",
            ],
        ),
        "selector:argument:x": delegate("numeric"),
        "selector:argument:y": delegate("numeric"),
        "selector:argument:z": delegate("numeric"),
        "selector:argument:distance": delegate("range"),
        "selector:argument:dx": delegate("numeric"),
        "selector:argument:dy": delegate("numeric"),
        "selector:argument:dz": delegate("numeric"),
        "selector:argument:scores": parse_selector_scores,
        "selector:argument:tag": delegate("word"),
        "selector:argument:team": delegate("word"),
        "selector:argument:limit": delegate("integer"),
        "selector:argument:sort": LiteralConstraint(
            parser=delegate("word"),
            values=[
                "nearest",
                "furthest",
                "random",
                "arbitrary",
            ],
        ),
        "selector:argument:level": delegate("integer_range"),
        "selector:argument:gamemode": LiteralConstraint(
            parser=delegate("word"),
            values=[
                "adventure",
                "creative",
                "spectator",
                "survival",
            ],
        ),
        "selector:argument:name": delegate("phrase"),
        "selector:argument:x_rotation": delegate("range"),
        "selector:argument:y_rotation": delegate("range"),
        "selector:argument:type": delegate("resource_location_or_tag"),
        "selector:argument:nbt": delegate("nbt_compound"),
        "selector:argument:advancements": parse_selector_advancements,
        "selector:argument:predicate": delegate("resource_location"),
        ################################################################################
        # Command
        ################################################################################
        "root": parse_root,
        "command": parse_command,
        "command:argument": parse_argument,
        "command:argument:brigadier:bool": delegate("bool"),
        "command:argument:brigadier:double": MinMaxConstraint(delegate("numeric")),
        "command:argument:brigadier:float": MinMaxConstraint(delegate("numeric")),
        "command:argument:brigadier:integer": MinMaxConstraint(delegate("integer")),
        "command:argument:brigadier:long": MinMaxConstraint(delegate("integer")),
        "command:argument:brigadier:string": parse_string_argument,
        "command:argument:minecraft:angle": RestrictCoordinateConstraint(
            parser=delegate("coordinate"),
            disallow=["local"],
        ),
        "command:argument:minecraft:block_pos": Vector3Parser(delegate("coordinate")),
        "command:argument:minecraft:block_predicate": delegate("block_predicate"),
        "command:argument:minecraft:block_state": delegate("block_state"),
        "command:argument:minecraft:color": LiteralConstraint(
            parser=delegate("word"),
            values=[
                "reset",
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
            ],
        ),
        "command:argument:minecraft:column_pos": Vector2Parser(
            coordinate_parser=RestrictCoordinateConstraint(
                parser=delegate("integer_coordinate"),
                disallow=["local"],
            ),
        ),
        "command:argument:minecraft:component": delegate("json"),
        "command:argument:minecraft:dimension": delegate("resource_location"),
        "command:argument:minecraft:entity": EntityParser(
            selector_parser=SelectorTypeConstraint(
                SelectorAmountConstraint(delegate("selector"))
            ),
        ),
        "command:argument:minecraft:entity_anchor": LiteralConstraint(
            parser=delegate("word"),
            values=["eyes", "feet"],
        ),
        "command:argument:minecraft:entity_summon": delegate("resource_location"),
        "command:argument:minecraft:float_range": delegate("range"),
        "command:argument:minecraft:function": delegate("resource_location_or_tag"),
        "command:argument:minecraft:game_profile": EntityParser(
            selector_parser=SelectorPlayerConstraint(delegate("selector")),
        ),
        "command:argument:minecraft:int_range": delegate("integer_range"),
        "command:argument:minecraft:item_enchantment": delegate("word"),
        "command:argument:minecraft:item_predicate": delegate("item_predicate"),
        "command:argument:minecraft:item_slot": delegate("word"),
        "command:argument:minecraft:item_stack": delegate("item_stack"),
        "command:argument:minecraft:message": parse_message,
        "command:argument:minecraft:mob_effect": delegate("resource_location"),
        "command:argument:minecraft:nbt_compound_tag": delegate("nbt_compound"),
        "command:argument:minecraft:nbt_path": delegate("nbt_path"),
        "command:argument:minecraft:nbt_tag": delegate("nbt"),
        "command:argument:minecraft:objective": delegate("objective"),
        "command:argument:minecraft:objective_criteria": delegate("literal"),
        "command:argument:minecraft:operation": LiteralConstraint(
            parser=delegate("literal"),
            values=[
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
        ),
        "command:argument:minecraft:particle": delegate("particle"),
        "command:argument:minecraft:resource_location": delegate("resource_location"),
        "command:argument:minecraft:rotation": Vector2Parser(
            coordinate_parser=RestrictCoordinateConstraint(
                parser=delegate("coordinate"),
                disallow=["local"],
            ),
        ),
        "command:argument:minecraft:score_holder": ScoreHolderParser(
            entity_parser=EntityParser(
                selector_parser=SelectorAmountConstraint(delegate("selector")),
            ),
        ),
        "command:argument:minecraft:scoreboard_slot": delegate("word"),
        "command:argument:minecraft:swizzle": delegate("swizzle"),
        "command:argument:minecraft:team": delegate("team"),
        "command:argument:minecraft:time": delegate("time"),
        "command:argument:minecraft:uuid": delegate("uuid"),
        "command:argument:minecraft:vec2": Vector2Parser(
            coordinate_parser=delegate("coordinate"),
        ),
        "command:argument:minecraft:vec3": Vector3Parser(
            coordinate_parser=delegate("coordinate"),
        ),
    }


def get_parsers(version: VersionNumber = "1.17") -> Dict[str, Parser]:
    """Return parsers for a specific version."""
    version = split_version(version)

    parsers = get_default_parsers()

    if version < (1, 18):
        parsers["objective"] = LengthConstraint(parsers["objective"], 16)
        parsers["player_name"] = LengthConstraint(parsers["player_name"], 40)

    return parsers


def get_stream_spec(stream: TokenStream) -> CommandSpec:
    """Return the command specification associated with the token stream."""
    return stream.data["spec"]


def get_stream_scope(stream: TokenStream) -> Tuple[str, ...]:
    """Return the current scope associated with the token stream."""
    return stream.data.get("scope", ())


def get_stream_properties(stream: TokenStream) -> Dict[str, Any]:
    """Return the current command node properties associated with the token stream."""
    return stream.data.get("properties", {})


def get_stream_multiline(stream: TokenStream) -> bool:
    """Return whether the token stream is currently parsing in multiline mode."""
    return stream.data.get("multiline", False)


def get_stream_line_indentation(stream: TokenStream) -> int:
    """Return the indentation level associated with the current line."""
    return stream.data.get("line_indentation", stream.indentation[-1])


class UnrecognizedParser(MechaError):
    """Raised when delegating to an unrecognized parser."""

    parser: str

    def __init__(self, parser: str):
        super().__init__(parser)
        self.parser = parser


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


def consume_line_continuation(stream: TokenStream) -> bool:
    """Consume newlines and leading whitespace if there's a line continuation."""
    level = get_stream_line_indentation(stream)
    multiline = get_stream_multiline(stream)

    if not multiline:
        return False

    with stream.checkpoint() as commit:
        if list(stream.collect("newline")):
            with stream.intercept("whitespace"):
                if (
                    (whitespace := stream.get("whitespace"))
                    and not stream.get("eof")
                    and level < len(whitespace.value.expandtabs())
                ):
                    commit()
                    return True

    return False


def parse_root(stream: TokenStream) -> AstRoot:
    """Parse root."""
    start = stream.peek()

    if not start:
        node = AstRoot(commands=AstChildren())
        return set_location(node, SourceLocation(0, 1, 1))

    commands: List[AstCommand] = []

    with stream.ignore("comment"):
        for _ in stream.peek_until():
            if stream.get("newline"):
                continue
            if stream.get("eof"):
                break
            commands.append(delegate("command", stream))

    node = AstRoot(commands=AstChildren(commands))
    return set_location(node, start, stream.current)


def parse_command(stream: TokenStream) -> AstCommand:
    """Parse command."""
    spec = get_stream_spec(stream)
    scope = get_stream_scope(stream)
    level = get_stream_line_indentation(stream)

    tree = spec.tree.get(scope)

    arguments: List[AstNode] = []
    reached_terminal = False

    with stream.checkpoint():
        location = stream.expect().location
        end_location = location

    while tree and tree.children:
        with stream.checkpoint() as commit:
            literal = stream.expect("literal")

            if child := tree.get_literal(literal.value):
                if not child.children:
                    if stream.peek():
                        stream.expect("newline", "eof")
                    reached_terminal = True

                end_location = literal.end_location
                scope = scope + (literal.value,)
                tree = child

                commit()

        if commit.rollback and tree.children:
            for (name, child), alternative in stream.choose(*tree.children.items()):
                with alternative, stream.provide(
                    scope=scope + (name,),
                    line_indentation=level,
                ):
                    literal = None
                    argument = None

                    if child.type == "literal":
                        literal = stream.expect(("literal", name))
                    elif child.type == "argument":
                        argument = delegate("command:argument", stream)

                    if not child.children:
                        if stream.peek():
                            stream.expect("newline", "eof")
                        reached_terminal = True

                    if literal:
                        end_location = literal.end_location
                    elif argument:
                        arguments.append(argument)
                        end_location = argument.end_location

                    scope = stream.data["scope"]
                    tree = child

        if reached_terminal:
            break

        with stream.provide(line_indentation=level):
            if not consume_line_continuation(stream):
                if tree.executable and (
                    not stream.peek() or stream.get("newline", "eof")
                ):
                    break

        target = spec.tree.get(tree.redirect)
        recursive = target and target.subcommand

        if tree.subcommand or recursive:
            subcommand_scope = tree.redirect if tree.redirect is not None else scope
            with stream.provide(scope=subcommand_scope, line_indentation=level):
                node = delegate("command", stream)
                arguments.append(node)
                end_location = node.end_location
                scope += ("subcommand",)
                break

    node = AstCommand(identifier=":".join(scope), arguments=AstChildren(arguments))
    return set_location(node, location, end_location)


def parse_argument(stream: TokenStream) -> AstNode:
    """Parse argument."""
    spec = get_stream_spec(stream)
    scope = get_stream_scope(stream)

    tree = spec.tree.get(scope)

    if tree and tree.parser:
        with stream.provide(properties=tree.properties or {}):
            return delegate(f"command:argument:{tree.parser}", stream)

    raise ValueError(f"Missing argument parser in command tree {scope}.")


@dataclass
class MultilineParser:
    """Allow a parser to span over multiple lines."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        with stream.checkpoint(), stream.intercept("newline"):
            newline = stream.get("newline")

        if not newline and get_stream_multiline(stream):
            with stream.ignore("newline"):
                return self.parser(stream)

        return self.parser(stream)


def parse_bool(stream: TokenStream) -> AstBool:
    """Parse bool."""
    with stream.syntax(literal=r"\w+"):
        token = stream.expect_any(("literal", "true"), ("literal", "false"))
    node = AstBool(value=token.value == "true")
    return set_location(node, token)


@dataclass
class NumericParser:
    """Parser for numeric values."""

    name: str = "number"
    pattern: str = NUMBER_PATTERN

    def __call__(self, stream: TokenStream) -> Any:
        with stream.syntax(**{self.name: self.pattern}):
            stream.expect(self.name)
        return self.create_node(stream)

    def create_node(self, stream: TokenStream) -> Any:
        """Create the ast node."""
        token = stream.current
        node = AstNumber(value=string_to_number(token.value))
        return set_location(node, token)


@dataclass
class CoordinateParser(NumericParser):
    """Parser for coordinates."""

    name: str = "coordinate"
    pattern: str = r"[~^]?" + NUMBER_PATTERN + r"|[~^]"

    def create_node(self, stream: TokenStream) -> Any:
        token = stream.current
        value = token.value

        if token.value.startswith("~"):
            coordinate_type = "relative"
            value = value[1:]
        elif token.value.startswith("^"):
            coordinate_type = "local"
            value = value[1:]
        else:
            coordinate_type = "absolute"

        if not value:
            value = "0"

        node = AstCoordinate(type=coordinate_type, value=string_to_number(value))
        return set_location(node, token)


@dataclass
class IntegerConstraint:
    """Constraint that disallows decimal numeric values."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        node: AstNumber = self.parser(stream)

        if not isinstance(node.value, int):
            raise node.emit_error(InvalidSyntax("Expected integer value."))

        return node


@dataclass
class MinMaxConstraint:
    """Constraint that checks that the value conforms to the min and max properties."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        properties = get_stream_properties(stream)
        node: AstNumber = self.parser(stream)

        if "min" in properties and node.value < properties["min"]:
            exc = InvalidSyntax(f"Expected value to be at least {properties['min']}.")
            raise node.emit_error(exc)
        if "max" in properties and node.value > properties["max"]:
            exc = InvalidSyntax(f"Expected value to be at most {properties['max']}.")
            raise node.emit_error(exc)

        return node


@dataclass
class RestrictCoordinateConstraint:
    """Constraint that disallows certain types of coordinates."""

    parser: Parser
    disallow: List[Literal["absolute", "relative", "local"]]

    def __call__(self, stream: TokenStream) -> Any:
        node: AstCoordinate = self.parser(stream)

        if node.type in self.disallow:
            exc = InvalidSyntax(f"Specifying {node.type} coordinates not allowed.")
            raise node.emit_error(exc)

        return node


@dataclass
class StringParser:
    """Parser for string values."""

    type: Literal["word", "phrase", "greedy"]
    quote_helper: QuoteHelper = field(default_factory=QuoteHelper)

    def __call__(self, stream: TokenStream) -> Any:
        if self.type == "greedy":
            with stream.intercept("whitespace"):
                while stream.get("whitespace"):
                    continue
            with stream.syntax(line=r".+"):
                token = stream.expect("line")
            node = AstLiteral(value=token.value)
        else:
            with stream.syntax(
                word=r"[0-9A-Za-z_\.\+\-]+",
                quoted_string=r'"(?:\\.|[^\\\n])*?"' "|" r"'(?:\\.|[^\\\n])*?'",
            ):
                if self.type == "word":
                    token = stream.expect("word")
                    node = AstLiteral(value=token.value)
                else:
                    token = stream.expect_any("word", "quoted_string")
                    node = AstString(value=self.quote_helper.unquote_string(token))
        return set_location(node, token)


def parse_string_argument(stream: TokenStream) -> Any:
    """Parse string argument."""
    properties = get_stream_properties(stream)
    string_type = properties["type"]

    if string_type not in ["word", "phrase", "greedy"]:
        raise ValueError(f"Invalid string type {string_type!r}.")

    return delegate(string_type, stream)


@dataclass
class Vector2Parser:
    """Parser for vector2."""

    coordinate_parser: Parser

    def __call__(self, stream: TokenStream) -> AstVector2:
        x = self.coordinate_parser(stream)
        y = self.coordinate_parser(stream)

        node = AstVector2(x=x, y=y)
        return set_location(node, x, y)


@dataclass
class Vector3Parser:
    """Parser for vector3."""

    coordinate_parser: Parser

    def __call__(self, stream: TokenStream) -> AstVector3:
        x = self.coordinate_parser(stream)
        y = self.coordinate_parser(stream)
        z = self.coordinate_parser(stream)

        node = AstVector3(x=x, y=y, z=z)
        return set_location(node, x, z)


@dataclass
class JsonParser:
    """Parser for json values."""

    quote_helper: QuoteHelper = field(
        default_factory=lambda: QuoteHelperWithUnicode(
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
            number=r"-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?\b",
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
                    key_node = AstJsonObjectKey(
                        value=self.quote_helper.unquote_string(key),
                    )
                    key_node = set_location(key_node, key)

                    stream.expect("colon")

                    value_node = self(stream)

                    entry_node = AstJsonObjectEntry(key=key_node, value=value_node)
                    entries.append(set_location(entry_node, key_node, value_node))

                    if not stream.get("comma"):
                        break

                close_curly = stream.expect(("curly", "}"))

                node = AstJsonObject(entries=AstChildren(entries))
                return set_location(node, curly, close_curly)

            elif bracket:
                elements: List[AstJson] = []

                for _ in stream.peek_until(("bracket", "]")):
                    elements.append(self(stream))

                    if not stream.get("comma"):
                        stream.expect(("bracket", "]"))
                        break

                node = AstJsonArray(elements=AstChildren(elements))
                return set_location(node, bracket, stream.current)

            if null:
                value = None
            elif true:
                value = True
            elif false:
                value = False
            elif string:
                value = self.quote_helper.unquote_string(string)
            elif number:
                value = string_to_number(number.value)

            node = AstJsonValue(value=value)  # type: ignore
            return set_location(node, stream.current)


@dataclass
class TypeConstraint:
    """Constraint that only allows specific instances."""

    parser: Parser
    type: Union[Type[Any], Tuple[Type[Any], ...]]
    message: str

    def __call__(self, stream: TokenStream) -> Any:
        node = self.parser(stream)

        if not isinstance(node, self.type):
            raise node.emit_error(InvalidSyntax(self.message))

        return node


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

    quote_helper: QuoteHelper = field(
        default_factory=lambda: QuoteHelper(
            escape_sequences={
                r"\\": "\\",
            }
        )
    )

    def __call__(self, stream: TokenStream) -> AstNbt:
        with stream.syntax(
            array=r"\[[BIL];",
            curly=r"\{|\}",
            bracket=r"\[|\]",
            quoted_string=r'"(?:\\.|[^\\\n])*?"' "|" r"'(?:\\.|[^\\\n])*?'",
            number=r"[+-]?(?:[0-9]*?\.[0-9]+|[0-9]+\.[0-9]*?|[1-9][0-9]*|0)(?:[eE][+-]?[0-9]+)?[bslfdBSLFD]?\b",
            string=r"[a-zA-Z0-9._+-]+",
            colon=r":",
            comma=r",",
        ):
            curly, bracket, array, number, string, quoted_string = stream.expect(
                ("curly", "{"),
                ("bracket", "["),
                "array",
                "number",
                "string",
                "quoted_string",
            )

            if curly:
                entries: List[AstNbtCompoundEntry] = []

                for key in stream.collect_any("number", "string", "quoted_string"):
                    key_node = AstNbtCompoundKey(
                        value=self.quote_helper.unquote_string(key),
                    )
                    key_node = set_location(key_node, key)

                    stream.expect("colon")

                    value_node = self(stream)

                    entry_node = AstNbtCompoundEntry(key=key_node, value=value_node)
                    entries.append(set_location(entry_node, key_node, value_node))

                    if not stream.get("comma"):
                        break

                close_curly = stream.expect(("curly", "}"))

                node = AstNbtCompound(entries=AstChildren(entries))
                return set_location(node, curly, close_curly)

            elif bracket or array:
                elements: List[AstNbt] = []

                for _ in stream.peek_until(("bracket", "]")):
                    elements.append(self(stream))

                    if not stream.get("comma"):
                        stream.expect(("bracket", "]"))
                        break

                if array:
                    if array.value[1] == "B":
                        node = AstNbtByteArray(elements=AstChildren(elements))
                        element_type = Byte  # type: ignore
                        msg = "Expected all elements to be bytes."
                    elif array.value[1] == "I":
                        node = AstNbtIntArray(elements=AstChildren(elements))
                        element_type = Int  # type: ignore
                        msg = "Expected all elements to be integers."
                    else:
                        node = AstNbtLongArray(elements=AstChildren(elements))
                        element_type = Long  # type: ignore
                        msg = "Expected all elements to be long integers."
                else:
                    node = AstNbtList(elements=AstChildren(elements))
                    if node.elements:
                        if isinstance(elements[0], AstNbtValue):
                            element_type = type(elements[0].value)
                        else:
                            element_type = type(elements[0])
                    else:
                        element_type = None
                    msg = "Expected all elements to have the same type."

                node = set_location(node, bracket or array, stream.current)

                if element_type:
                    for element in node.elements:
                        if (
                            type(element.value) is not element_type
                            if isinstance(element, AstNbtValue)
                            else type(element) is not element_type
                        ):
                            raise element.emit_error(InvalidSyntax(msg))

                return node

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
                value = String(self.quote_helper.unquote_string(quoted_string))  # type: ignore

            node = AstNbtValue(value=value)  # type: ignore
            return set_location(node, stream.current)


@dataclass
class AdjacentConstraint:
    """Constraint that ensures that there are no whitespace separators."""

    parser: Parser
    hint: str

    def __call__(self, stream: TokenStream) -> Any:
        with stream.syntax(hint=self.hint), stream.intercept("whitespace"):
            token = stream.peek()
            if not token or not token.match("hint"):
                return None
        return self.parser(stream)


@dataclass
class ResourceLocationParser:
    """Parser for resource locations."""

    def __call__(self, stream: TokenStream) -> AstResourceLocation:
        with stream.syntax(resource_location=r"#?(?:[0-9a-z_\-\.]+:)?[0-9a-z_./-]+"):
            token = stream.expect("resource_location")
            value = token.value
            location = token.location

            if is_tag := value.startswith("#"):
                value = value[1:]
                location = location.with_horizontal_offset(1)

            namespace, _, path = value.rpartition(":")

            if not namespace:
                namespace = None

            node = AstResourceLocation(is_tag=is_tag, namespace=namespace, path=path)
            return set_location(node, token)


@dataclass
class NoTagConstraint:
    """Constraint that disallows resource locations refering to tags."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        node: AstResourceLocation = self.parser(stream)

        if node.is_tag:
            raise node.emit_error(
                InvalidSyntax(f"Specifying a tag is not allowed {node.get_value()!r}.")
            )

        return node


@dataclass
class CommentDisambiguation:
    """Reset the stream to the last non-comment token."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        with stream.intercept("comment"):
            consume_line_continuation(stream)

        with stream.checkpoint() as commit:
            last_comment = None

            while stream.index >= 0 and stream.current.match(
                "whitespace",
                "newline",
                "comment",
                "indent",
                "dedent",
            ):
                if stream.current.match("comment"):
                    last_comment = stream.current
                stream.index -= 1

            if last_comment:
                commit()

        stream.generator = stream.generate_tokens()

        return self.parser(stream)


@dataclass
class BlockParser:
    """Parser for minecraft blocks."""

    resource_location_parser: Parser
    block_states_parser: Parser

    def __call__(self, stream: TokenStream) -> AstBlock:
        identifier = self.resource_location_parser(stream)

        location = identifier.location
        end_location = identifier.end_location

        if block_states := self.block_states_parser(stream):
            end_location = stream.current.end_location
        else:
            block_states = AstChildren()

        data_tags = delegate("adjacent_nbt_compound", stream)

        node = AstBlock(
            identifier=identifier,
            block_states=block_states,
            data_tags=data_tags,
        )
        return set_location(node, location, data_tags if data_tags else end_location)


def parse_block_states(stream: TokenStream) -> AstChildren[AstBlockState]:
    """Parser for minecraft block state."""
    block_states: List[AstBlockState] = []

    with stream.syntax(
        bracket=r"\[|\]",
        equal=r"=",
        comma=r",",
    ):
        stream.expect(("bracket", "["))

        for _ in stream.peek_until(("bracket", "]")):
            key_node = delegate("phrase", stream)
            stream.expect("equal")
            value_node = delegate("phrase", stream)

            entry_node = AstBlockState(key=key_node, value=value_node)
            entry_node = set_location(entry_node, key_node, value_node)
            block_states.append(entry_node)

            if not stream.get("comma"):
                stream.expect(("bracket", "]"))
                break

    return AstChildren(block_states)


@dataclass
class ItemParser:
    """Parser for minecraft items."""

    resource_location_parser: Parser

    def __call__(self, stream: TokenStream) -> AstItem:
        identifier = self.resource_location_parser(stream)
        location = identifier.location
        end_location = identifier.end_location

        data_tags = delegate("adjacent_nbt_compound", stream)

        node = AstItem(identifier=identifier, data_tags=data_tags)
        return set_location(node, location, data_tags if data_tags else end_location)


@dataclass
class NoBlockStatesConstraint:
    """Constraint that disallows block states."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        node: AstBlock = self.parser(stream)

        if node.block_states:
            raise node.emit_error(InvalidSyntax("Specifying block states not allowed."))

        return node


@dataclass
class NoDataTagsConstraint:
    """Constraint that disallows data tags."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        node: AstBlock = self.parser(stream)

        if node.data_tags:
            raise node.emit_error(InvalidSyntax("Specifying data tags not allowed."))

        return node


@dataclass
class LiteralParser:
    """Parser for simple literal values."""

    name: str
    pattern: str = r"\S+"

    def __call__(self, stream: TokenStream) -> AstLiteral:
        with stream.syntax(**{self.name: self.pattern}):
            token = stream.expect(self.name)
        node = AstLiteral(value=token.value)
        return set_location(node, token)


@dataclass
class LiteralConstraint:
    """Constraint that only allows a set of predefined values."""

    parser: Parser
    values: List[Any]

    def __call__(self, stream: TokenStream) -> Any:
        node: AstLiteral = self.parser(stream)

        if node.value not in self.values:
            raise node.emit_error(InvalidSyntax(f"Unexpected value {node.value!r}."))

        return node


@dataclass
class RangeParser:
    """Parser for ranges."""

    pattern: str = fr"\.\.{NUMBER_PATTERN}|{NUMBER_PATTERN}\.\.(?:{NUMBER_PATTERN})?|{NUMBER_PATTERN}"

    def __call__(self, stream: TokenStream) -> AstRange:
        with stream.syntax(range=self.pattern):
            token = stream.expect("range")
            minimum, separator, maximum = token.value.partition("..")

            if not separator:
                maximum = minimum

            node = AstRange(
                min=string_to_number(minimum) if minimum else None,
                max=string_to_number(maximum) if maximum else None,
            )
            return set_location(node, token)


@dataclass
class IntegerRangeConstraint:
    """Constraint that disallows decimal ranges."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        node: AstRange = self.parser(stream)

        if isinstance(node.min, float) or isinstance(node.max, float):
            raise node.emit_error(InvalidSyntax("Expected integer range."))

        return node


@dataclass
class LengthConstraint:
    """Constraint that only allows up to a limited number of characters."""

    parser: Parser
    limit: int

    def __call__(self, stream: TokenStream) -> Any:
        node: AstLiteral = self.parser(stream)

        if len(node.value) > self.limit:
            exc = InvalidSyntax(f"Expected up to {self.limit} characters.")
            raise node.emit_error(exc)

        return node


def parse_swizzle(stream: TokenStream) -> AstLiteral:
    """Parse swizzle."""
    node = delegate("literal", stream)

    normalized = set(node.value[:3]) & {"x", "y", "z"}
    if not normalized or len(node.value) != len(normalized):
        raise node.emit_error(InvalidSyntax(f"Invalid swizzle {node.value!r}."))

    return node


@dataclass
class TimeParser(NumericParser):
    """Parser for time."""

    name: str = "time"
    pattern: str = NUMBER_PATTERN + r"[dst]?"

    def create_node(self, stream: TokenStream) -> Any:
        token = stream.current
        value = token.value

        if value.endswith(("d", "s", "t")):
            if value[-1] == "d":
                unit = "day"
            elif value[-1] == "s":
                unit = "second"
            else:
                unit = "tick"
            value = value[:-1]
        else:
            unit = "tick"

        node = AstTime(value=string_to_number(value), unit=unit)
        return set_location(node, token)


def parse_uuid(stream: TokenStream) -> AstUUID:
    """Parse uuid."""
    with stream.syntax(uuid="-".join([r"[a-fA-F0-9]+"] * 5)):
        token = stream.expect("uuid")
    a, b, c, d, e = token.value.split("-")
    node = AstUUID(value=UUID(f"{a:>08}-{b:>04}-{c:>04}-{d:>04}-{e:>012}"))
    return set_location(node, token)


@dataclass
class SelectorParser:
    """Parser for selectors."""

    def __call__(self, stream: TokenStream) -> AstSelector:
        with stream.syntax(
            selector=r"@[praes]\[?",
            bracket=r"\[|\]",
            comma=r",",
        ):
            token = stream.expect("selector")
            variable = token.value[1]
            location = token.location
            end_location = token.end_location

            arguments: List[AstSelectorArgument] = []

            if token.value.endswith("["):
                for _ in stream.peek_until(("bracket", "]")):
                    arguments.append(delegate("selector:argument", stream))
                    if not stream.get("comma"):
                        stream.expect(("bracket", "]"))
                        break

                end_location = stream.current.end_location

        node = AstSelector(
            variable=variable,  # type: ignore
            arguments=AstChildren(arguments),
        )
        return set_location(node, location, end_location)


@dataclass
class SelectorArgumentParser:
    """Parser for selector arguments."""

    def __call__(self, stream: TokenStream) -> Any:
        with stream.syntax(
            equal=r"=",
            exclamation=r"!",
        ):
            key_node = delegate("phrase", stream)
            argument = key_node.value

            stream.expect("equal")

            inverted = stream.get("exclamation") is not None

            hint = stream.peek()

            if hint and hint.match("comma", ("bracket", "]")):
                value_node = None
            else:
                try:
                    value_node = delegate(f"selector:argument:{argument}", stream)
                except UnrecognizedParser as exc:
                    if not exc.parser.startswith("selector:argument:"):
                        raise
                    syntax_exc = InvalidSyntax(
                        f"Invalid selector argument {argument!r}."
                    )
                    raise key_node.emit_error(syntax_exc) from exc

        node = AstSelectorArgument(inverted=inverted, key=key_node, value=value_node)
        return set_location(node, key_node, value_node)


@dataclass
class SelectorArgumentInvertConstraint:
    """Constraint that only allows inverting a specific set of arguments."""

    parser: Parser
    allow_invert: List[str]

    def __call__(self, stream: TokenStream) -> Any:
        node: AstSelectorArgument = self.parser(stream)

        if node.inverted and node.key.value not in self.allow_invert:
            exc = InvalidSyntax(f"Can not invert argument {node.key.value!r}.")
            raise node.emit_error(exc)

        return node


@dataclass
class SelectorArgumentNoValueConstraint:
    """Constraint that only allows a specific set of arguments to have no associated value."""

    parser: Parser
    allow_no_value: List[str]

    def __call__(self, stream: TokenStream) -> Any:
        node: AstSelectorArgument = self.parser(stream)

        if not node.value and node.key.value not in self.allow_no_value:
            exc = InvalidSyntax(f"Argument {node.key.value!r} must have a value.")
            raise node.emit_error(exc)

        return node


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

        for key in stream.collect("objective"):
            key_node = AstLiteral(value=key.value)
            key_node = set_location(key_node, key)

            stream.expect("equal")

            value_node = delegate("integer_range", stream)

            match_node = AstSelectorScoreMatch(key=key_node, value=value_node)
            scores.append(set_location(match_node, key_node, value_node))

            if not stream.get("comma"):
                break

        close_curly = stream.expect(("curly", "}"))

        node = AstSelectorScores(scores=AstChildren(scores))
        return set_location(node, curly, close_curly)


def parse_selector_advancements(stream: TokenStream) -> AstSelectorAdvancements:
    """Parse selector advancements."""
    with stream.syntax(curly=r"\{|\}", equal=r"=", comma=r","):
        curly = stream.expect(("curly", "{"))

        advancements: List[AstSelectorAdvancementMatch] = []

        for _ in stream.peek_until(("curly", "}")):
            key_node = delegate("resource_location", stream)
            stream.expect("equal")

            if stream.get("curly"):
                predicates: List[AstSelectorAdvancementPredicateMatch] = []

                for _ in stream.peek_until(("curly", "}")):
                    pkey = delegate("word", stream)
                    stream.expect("equal")
                    pvalue = delegate("bool", stream)

                    predicate_node = AstSelectorAdvancementPredicateMatch(
                        key=pkey,
                        value=pvalue,
                    )
                    predicates.append(set_location(predicate_node, pkey, pvalue))

                    if not stream.get("comma"):
                        stream.expect(("curly", "}"))
                        break

                value_node = AstChildren(predicates)
            else:
                value_node = delegate("bool", stream)

            match_node = AstSelectorAdvancementMatch(key=key_node, value=value_node)
            advancements.append(set_location(match_node, key_node, value_node))

            if not stream.get("comma"):
                stream.expect(("curly", "}"))
                break

        node = AstSelectorAdvancements(advancements=AstChildren(advancements))
        return set_location(node, curly, stream.current)


@dataclass
class SelectorPlayerConstraint:
    """Constraint that disallows non player-type entities."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        node: AstSelector = self.parser(stream)

        is_player = node.variable in "pras"

        for argument in node.arguments:
            if argument.key.value in ["gamemode", "level"]:
                is_player = True
            if argument.key.value == "type":
                is_player = (
                    not argument.inverted
                    and isinstance(entity_type := argument.value, AstResourceLocation)
                    and entity_type.get_canonical_value() == "minecraft:player"
                )

        if not is_player:
            exc = InvalidSyntax("Expected player-type entity selector.")
            raise node.emit_error(exc)

        return node


@dataclass
class SelectorTypeConstraint:
    """Constraint that only allows selectors that match the type property."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        properties = get_stream_properties(stream)
        selector_type = properties["type"]

        if selector_type not in ["players", "entities"]:
            raise ValueError(f"Invalid selector type {selector_type}.")

        if selector_type == "entities":
            return self.parser(stream)

        return SelectorPlayerConstraint(self.parser)(stream)


@dataclass
class SelectorSingleConstraint:
    """Constraint that disallows selectors that target more than one entity."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        node: AstSelector = self.parser(stream)

        is_single = node.variable in "prs"

        for arg in node.arguments:
            if arg.key.value == "limit":
                is_single = arg.value == AstNumber(value=1)

        if not is_single:
            exc = InvalidSyntax("Expected entity selector targeting a single entity.")
            raise node.emit_error(exc)

        return node


@dataclass
class SelectorAmountConstraint:
    """Constraint that only allows selectors that match the amount property."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        properties = get_stream_properties(stream)

        amount = properties["amount"]

        if amount not in ["single", "multiple"]:
            raise ValueError(f"Invalid selector amount {amount}.")

        if amount == "multiple":
            return self.parser(stream)

        return SelectorSingleConstraint(self.parser)(stream)


@dataclass
class EntityParser:
    """Parser for entities."""

    selector_parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        """Parse entity."""
        with stream.syntax(literal=r"\S+"):
            hint = stream.peek()

        if hint:
            if hint.value.startswith("@"):
                return self.selector_parser(stream)

            if hint.value.count("-") == 4:
                with stream.alternative():
                    return delegate("uuid", stream)

        return delegate("player_name", stream)


@dataclass
class ScoreHolderParser:
    """Parser for score holder."""

    entity_parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        with stream.syntax(wildcard=r"\*"):
            if token := stream.get("wildcard"):
                node = AstLiteral(value=token.value)
                return set_location(node, token)
        return self.entity_parser(stream)


def parse_message(stream: TokenStream) -> AstMessage:
    """Parse message."""
    multiline = get_stream_multiline(stream)

    with stream.intercept("whitespace"):
        stream.get("whitespace")

    with stream.intercept("newline"), stream.syntax(
        selector=r"@[praes]",
        text=r"[^\n@]+",
    ):
        fragments: List[Any] = []

        while True:
            selector, text = stream.expect("selector", "text")

            if selector:
                stream.index -= 1
                with stream.ignore("newline") if multiline else nullcontext():
                    with stream.syntax(text=None):
                        fragments.append(delegate("selector", stream))
            elif text:
                text_node = AstLiteral(value=text.value)
                text_node = set_location(text_node, text)
                fragments.append(text_node)

            with stream.syntax(text=None):
                if consume_line_continuation(stream):
                    whitespace_node = AstLiteral(value=" ")
                    whitespace_node = set_location(
                        whitespace_node,
                        stream.current.end_location.with_horizontal_offset(-1),
                        stream.current.end_location,
                    )
                    fragments.append(whitespace_node)
                else:
                    with stream.checkpoint():
                        if stream.get("newline", "eof"):
                            break

    node = AstMessage(fragments=AstChildren(fragments))
    return set_location(node, fragments[0], fragments[-1])


@dataclass
class NbtPathParser:
    quote_helper: QuoteHelper = field(
        default_factory=lambda: QuoteHelper(
            escape_sequences={
                r"\\": "\\",
            }
        )
    )

    def __call__(self, stream: TokenStream) -> AstNbtPath:
        components: List[Any] = []

        with stream.syntax(
            dot=r"\.",
            curly=r"\{|\}",
            bracket=r"\[|\]",
            quoted_string=r'"(?:\\.|[^\\\n])*?"' "|" r"'(?:\\.|[^\\\n])*?'",
            string=r"[a-zA-Z0-9_+-]+",
        ):
            components.extend(self.parse_modifiers(stream))

            while not components or stream.get("dot"):
                quoted_string, string = stream.expect("quoted_string", "string")

                if quoted_string:
                    component_node = AstString(
                        value=self.quote_helper.unquote_string(quoted_string),
                    )
                    components.append(set_location(component_node, quoted_string))
                elif string:
                    component_node = AstString(value=string.value)
                    components.append(set_location(component_node, string))

                components.extend(self.parse_modifiers(stream))

        if not components:
            raise stream.emit_error(InvalidSyntax("Empty nbt path not allowed."))

        node = AstNbtPath(components=AstChildren(components))
        return set_location(node, components[0], components[-1])

    def parse_modifiers(self, stream: TokenStream) -> Iterator[Any]:
        """Parse named tag modifiers."""
        hint = stream.peek()

        if hint and hint.match(("curly", "{")):
            yield delegate("nbt_compound", stream)
            return

        while bracket := stream.get(("bracket", "[")):
            index = None

            hint = stream.peek()
            if hint and hint.match(("curly", "{")):
                index = delegate("nbt_compound", stream)
            elif hint and not hint.match(("bracket", "]")):
                index = delegate("integer", stream)

            close_bracket = stream.expect(("bracket", "]"))

            subscript_node = AstNbtPathSubscript(index=index)
            yield set_location(subscript_node, bracket, close_bracket)


def parse_particle(stream: TokenStream) -> AstParticle:
    """Parse particle."""
    name: AstResourceLocation = delegate("resource_location", stream)
    parameters = None

    try:
        parameters = delegate(f"particle:{name.get_canonical_value()}", stream)
    except UnrecognizedParser as exc:
        if not exc.parser.startswith("particle:"):
            raise

    node = AstParticle(name=name, parameters=parameters)
    return set_location(node, name, parameters if parameters else name)


@dataclass
class AggregateParser:
    """Parser that creates a node by parsing the given fields one after the other."""

    type: Type[AstNode]
    fields: Dict[str, Parser]

    def __call__(self, stream: TokenStream) -> Any:
        values = [(name, parser(stream)) for name, parser in self.fields.items()]
        node = self.type(**dict(values))
        return set_location(node, values[0][1], values[-1][1])


@dataclass
class SingleLineConstraint:
    """Constraint that prevents parsing across multiple lines."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        with stream.intercept("newline"):
            return self.parser(stream)


@dataclass
class ResetSyntaxParser:
    """Parser that resets the syntax rules before delegating to a subparser."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        with stream.reset_syntax():
            return self.parser(stream)
