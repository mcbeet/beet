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
    "TypeConstraint",
    "JsonParser",
    "JsonObjectParser",
    "NbtParser",
    "NbtCompoundParser",
    "AdjacentConstraint",
    "ResourceLocationParser",
    "NoTagConstraint",
    "BlockParser",
    "BlockStatesParser",
    "ItemParser",
    "NoBlockStatesConstraint",
    "NoDataTagsConstraint",
    "BasicLiteralParser",
    "RangeParser",
    "IntegerRangeConstraint",
    "LengthConstraint",
    "CommentDisambiguation",
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
    "parse_wildcard",
    "parse_message",
    "NbtPathParser",
    "parse_particle",
    "AggregateParser",
    "SingleLineConstraint",
    "AlternativeParser",
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

from beet import LATEST_MINECRAFT_VERSION
from beet.core.utils import VersionNumber, split_version
from nbtlib import Byte, Double, Float, Int, Long, OutOfRange, Short, String
from tokenstream import InvalidSyntax, SourceLocation, TokenStream, set_location

from .ast import (
    AstAdvancementPredicate,
    AstBlock,
    AstBlockMarkerParticleParameters,
    AstBlockParticleParameters,
    AstBlockState,
    AstBool,
    AstChildren,
    AstColor,
    AstColorReset,
    AstCommand,
    AstCoordinate,
    AstDustColorTransitionParticleParameters,
    AstDustParticleParameters,
    AstEntityAnchor,
    AstFallingDustParticleParameters,
    AstGamemode,
    AstGreedy,
    AstItem,
    AstItemParticleParameters,
    AstItemSlot,
    AstJson,
    AstJsonArray,
    AstJsonObject,
    AstJsonObjectEntry,
    AstJsonObjectKey,
    AstJsonValue,
    AstLiteral,
    AstMessage,
    AstMessageText,
    AstNbt,
    AstNbtByteArray,
    AstNbtCompound,
    AstNbtCompoundEntry,
    AstNbtCompoundKey,
    AstNbtIntArray,
    AstNbtList,
    AstNbtLongArray,
    AstNbtPath,
    AstNbtPathKey,
    AstNbtPathSubscript,
    AstNbtValue,
    AstNode,
    AstNumber,
    AstObjective,
    AstObjectiveCriteria,
    AstParticle,
    AstPlayerName,
    AstRange,
    AstResourceLocation,
    AstRoot,
    AstScoreboardOperation,
    AstScoreboardSlot,
    AstSelector,
    AstSelectorAdvancementMatch,
    AstSelectorAdvancementPredicateMatch,
    AstSelectorAdvancements,
    AstSelectorArgument,
    AstSelectorScoreMatch,
    AstSelectorScores,
    AstSortOrder,
    AstString,
    AstSwizzle,
    AstTeam,
    AstTime,
    AstUUID,
    AstVector2,
    AstVector3,
    AstVibrationParticleParameters,
    AstWildcard,
    AstWord,
)
from .config import CommandTree
from .error import MechaError
from .spec import CommandSpec, Parser
from .utils import JsonQuoteHelper, QuoteHelper, string_to_number

NUMBER_PATTERN: str = r"-?(?:\d+\.?\d*|\.\d+)"


def get_default_parsers() -> Dict[str, Parser]:
    """Return the default parsers."""
    json_parser = JsonParser()
    json_parser.object_entry_parser = delegate("json_object_entry")
    json_parser.array_element_parser = delegate("json_array_element")
    json_parser.recursive_parser = delegate("json")

    nbt_parser = NbtParser()
    nbt_parser.compound_entry_parser = delegate("nbt_compound_entry")
    nbt_parser.list_or_array_element_parser = delegate("nbt_list_or_array_element")
    nbt_parser.recursive_parser = delegate("nbt")

    return {
        ################################################################################
        # Primitives
        ################################################################################
        "bool": parse_bool,
        "numeric": NumericParser(),
        "integer": IntegerConstraint(delegate("numeric")),
        "coordinate": CoordinateParser(),
        "integer_coordinate": IntegerConstraint(delegate("coordinate")),
        "time": TimeParser(),
        "word": StringParser(type="word"),
        "phrase": StringParser(type="phrase"),
        "greedy": StringParser(type="greedy"),
        "json": json_parser,
        "json_object_entry": json_parser.parse_object_entry,
        "json_array_element": delegate("json"),
        "json_object": JsonObjectParser(delegate("json")),
        "nbt": nbt_parser,
        "nbt_compound_entry": nbt_parser.parse_compound_entry,
        "nbt_list_or_array_element": delegate("nbt"),
        "nbt_compound": NbtCompoundParser(delegate("nbt")),
        "adjacent_nbt_compound": AdjacentConstraint(delegate("nbt_compound"), r"\{"),
        "nbt_path": NbtPathParser(
            integer_parser=delegate("integer"),
            nbt_compound_parser=delegate("nbt_compound"),
        ),
        "range": RangeParser(),
        "integer_range": IntegerRangeConstraint(delegate("range")),
        "resource_location_or_tag": CommentDisambiguation(ResourceLocationParser()),
        "resource_location": NoTagConstraint(delegate("resource_location_or_tag")),
        "uuid": parse_uuid,
        "objective": BasicLiteralParser(AstObjective),
        "objective_criteria": BasicLiteralParser(AstObjectiveCriteria),
        "scoreboard_operation": BasicLiteralParser(AstScoreboardOperation),
        "player_name": CommentDisambiguation(BasicLiteralParser(AstPlayerName)),
        "scoreboard_slot": BasicLiteralParser(AstScoreboardSlot),
        "swizzle": BasicLiteralParser(AstSwizzle),
        "team": BasicLiteralParser(AstTeam),
        "advancement_predicate": BasicLiteralParser(AstAdvancementPredicate),
        "wildcard": parse_wildcard,
        "color": BasicLiteralParser(AstColor),
        "color_reset": BasicLiteralParser(AstColorReset),
        "sort_order": BasicLiteralParser(AstSortOrder),
        "gamemode": BasicLiteralParser(AstGamemode),
        "entity_anchor": BasicLiteralParser(AstEntityAnchor),
        "block_predicate": BlockParser(
            resource_location_parser=delegate("resource_location_or_tag"),
            block_states_parser=AdjacentConstraint(
                parser=MultilineParser(
                    BlockStatesParser(
                        key_parser=StringParser(type="phrase"),
                        value_parser=delegate("phrase"),
                    )
                ),
                hint=r"\[",
            ),
            data_tags_parser=delegate("adjacent_nbt_compound"),
        ),
        "block_state": BlockParser(
            resource_location_parser=delegate("resource_location"),
            block_states_parser=AdjacentConstraint(
                parser=MultilineParser(
                    BlockStatesParser(
                        key_parser=StringParser(type="phrase"),
                        value_parser=delegate("phrase"),
                    )
                ),
                hint=r"\[",
            ),
            data_tags_parser=delegate("adjacent_nbt_compound"),
        ),
        "item_predicate": ItemParser(
            resource_location_parser=delegate("resource_location_or_tag"),
            data_tags_parser=delegate("adjacent_nbt_compound"),
        ),
        "item_slot": BasicLiteralParser(AstItemSlot),
        "item_stack": ItemParser(
            resource_location_parser=delegate("resource_location"),
            data_tags_parser=delegate("adjacent_nbt_compound"),
        ),
        "message": parse_message,
        "block_pos": Vector3Parser(coordinate_parser=delegate("coordinate")),
        "column_pos": Vector2Parser(
            coordinate_parser=RestrictCoordinateConstraint(
                parser=delegate("integer_coordinate"),
                disallow=["local"],
            ),
        ),
        "rotation": Vector2Parser(
            coordinate_parser=RestrictCoordinateConstraint(
                parser=delegate("coordinate"),
                disallow=["local"],
            ),
        ),
        "vec2": Vector2Parser(coordinate_parser=delegate("coordinate")),
        "vec3": Vector3Parser(coordinate_parser=delegate("coordinate")),
        "entity": EntityParser(
            selector_parser=SelectorTypeConstraint(
                SelectorAmountConstraint(delegate("selector"))
            ),
        ),
        "score_holder": AlternativeParser(
            [
                EntityParser(SelectorAmountConstraint(delegate("selector"))),
                delegate("wildcard"),
            ]
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
        "particle:minecraft:block_marker": AggregateParser(
            type=AstBlockMarkerParticleParameters,
            fields={"block": delegate("block_state")},
        ),
        ################################################################################
        # Selector
        ################################################################################
        "selector": MultilineParser(SelectorParser()),
        "selector:argument": SelectorArgumentInvertConstraint(
            SelectorArgumentNoValueConstraint(
                SelectorArgumentParser(key_parser=StringParser(type="phrase")),
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
        "selector:argument:team": delegate("team"),
        "selector:argument:limit": delegate("integer"),
        "selector:argument:sort": delegate("sort_order"),
        "selector:argument:level": delegate("integer_range"),
        "selector:argument:gamemode": delegate("gamemode"),
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
        "command:argument:minecraft:block_pos": delegate("block_pos"),
        "command:argument:minecraft:block_predicate": MultilineParser(
            delegate("block_predicate")
        ),
        "command:argument:minecraft:block_state": MultilineParser(
            delegate("block_state")
        ),
        "command:argument:minecraft:color": AlternativeParser(
            [
                delegate("color"),
                delegate("color_reset"),
            ]
        ),
        "command:argument:minecraft:column_pos": delegate("column_pos"),
        "command:argument:minecraft:component": MultilineParser(delegate("json")),
        "command:argument:minecraft:dimension": delegate("resource_location"),
        "command:argument:minecraft:entity": delegate("entity"),
        "command:argument:minecraft:entity_anchor": delegate("entity_anchor"),
        "command:argument:minecraft:entity_summon": delegate("resource_location"),
        "command:argument:minecraft:float_range": delegate("range"),
        "command:argument:minecraft:function": delegate("resource_location_or_tag"),
        "command:argument:minecraft:game_profile": EntityParser(
            selector_parser=SelectorPlayerConstraint(delegate("selector")),
        ),
        "command:argument:minecraft:int_range": delegate("integer_range"),
        "command:argument:minecraft:item_enchantment": delegate("word"),
        "command:argument:minecraft:item_predicate": MultilineParser(
            delegate("item_predicate")
        ),
        "command:argument:minecraft:item_slot": delegate("item_slot"),
        "command:argument:minecraft:item_stack": MultilineParser(
            delegate("item_stack")
        ),
        "command:argument:minecraft:message": delegate("message"),
        "command:argument:minecraft:mob_effect": delegate("resource_location"),
        "command:argument:minecraft:nbt_compound_tag": MultilineParser(
            delegate("nbt_compound")
        ),
        "command:argument:minecraft:nbt_path": MultilineParser(delegate("nbt_path")),
        "command:argument:minecraft:nbt_tag": MultilineParser(delegate("nbt")),
        "command:argument:minecraft:objective": AlternativeParser(
            [
                delegate("objective"),
                delegate("wildcard"),
            ]
        ),
        "command:argument:minecraft:objective_criteria": delegate("objective_criteria"),
        "command:argument:minecraft:operation": delegate("scoreboard_operation"),
        "command:argument:minecraft:particle": delegate("particle"),
        "command:argument:minecraft:resource_location": delegate("resource_location"),
        "command:argument:minecraft:resource": delegate("resource_location"),
        "command:argument:minecraft:resource_or_tag": delegate(
            "resource_location_or_tag"
        ),
        "command:argument:minecraft:rotation": delegate("rotation"),
        "command:argument:minecraft:score_holder": delegate("score_holder"),
        "command:argument:minecraft:scoreboard_slot": delegate("scoreboard_slot"),
        "command:argument:minecraft:swizzle": delegate("swizzle"),
        "command:argument:minecraft:team": delegate("team"),
        "command:argument:minecraft:time": delegate("time"),
        "command:argument:minecraft:uuid": delegate("uuid"),
        "command:argument:minecraft:vec2": delegate("vec2"),
        "command:argument:minecraft:vec3": delegate("vec3"),
    }


def get_parsers(version: VersionNumber = LATEST_MINECRAFT_VERSION) -> Dict[str, Parser]:
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
        node = AstRoot(commands=AstChildren[AstCommand]())
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

    location = None
    end_location = None

    while tree:
        with stream.checkpoint() as commit:
            literal = stream.expect("literal")

            if child := tree.get_literal(literal.value):
                if not child.children:
                    if stream.peek():
                        stream.expect("newline", "eof")
                    reached_terminal = True

                if location is None:
                    location = literal.location
                end_location = literal.end_location
                scope = scope + (literal.value,)
                tree = child

                commit()

        if commit.rollback:
            choices: List[Tuple[str, CommandTree]] = list((tree.children or {}).items())
            choices.sort(key=lambda p: p[1].type != "argument")

            if tree.executable:
                choices.append(("", tree))

            for (name, child), alternative in stream.choose(*choices):
                with alternative, stream.provide(
                    scope=scope + (name,),
                    line_indentation=level,
                ):
                    literal = None
                    argument = None

                    if tree is child and tree.executable:
                        if stream.peek():
                            stream.expect("newline", "eof")
                        reached_terminal = True
                        continue

                    elif child.type == "literal":
                        literal = stream.expect(("literal", name))
                        if location is None:
                            location = literal.location

                    elif child.type == "argument":
                        argument = delegate("command:argument", stream)
                        if location is None:
                            location = argument.location

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
            consume_line_continuation(stream)

        target = spec.tree.get(tree.redirect)
        recursive = target and target.subcommand

        if tree.subcommand or recursive:
            if tree.executable and (not stream.peek() or stream.get("newline", "eof")):
                break
            subcommand_scope = tree.redirect if tree.redirect is not None else scope
            with stream.alternative(bool(target and target.children)), stream.provide(
                scope=subcommand_scope,
                line_indentation=level,
            ):
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
    pattern: str = rf"(?:[~^]?{NUMBER_PATTERN}|[~^])(?!\w|-|\.)"

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
        if isinstance(node := self.parser(stream), (AstNumber, AstCoordinate)):
            if not isinstance(node.value, int):
                raise node.emit_error(InvalidSyntax("Expected integer value."))
        return node


@dataclass
class MinMaxConstraint:
    """Constraint that checks that the value conforms to the min and max properties."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        properties = get_stream_properties(stream)

        if isinstance(node := self.parser(stream), AstNumber):
            if "min" in properties and node.value < properties["min"]:
                exc = InvalidSyntax(
                    f"Expected value to be at least {properties['min']}."
                )
                raise node.emit_error(exc)
            if "max" in properties and node.value > properties["max"]:
                exc = InvalidSyntax(
                    f"Expected value to be at most {properties['max']}."
                )
                raise node.emit_error(exc)

        return node


@dataclass
class RestrictCoordinateConstraint:
    """Constraint that disallows certain types of coordinates."""

    parser: Parser
    disallow: List[Literal["absolute", "relative", "local"]]

    def __call__(self, stream: TokenStream) -> Any:
        if isinstance(node := self.parser(stream), AstCoordinate):
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
            with stream.syntax(line=AstGreedy.regex.pattern):
                token = stream.expect("line")
            node = AstGreedy(value=token.value)
        else:
            with stream.syntax(
                word=AstWord.regex.pattern,
                quoted_string=r'"(?:\\.|[^\\\n])*?"' "|" r"'(?:\\.|[^\\\n])*?'",
            ):
                if self.type == "word":
                    token = stream.expect("word")
                    node = AstWord(value=token.value)
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
class JsonParser:
    """Parser for json values."""

    curly_pattern: str = r"\{|\}"
    bracket_pattern: str = r"\[|\]"
    string_pattern: str = r'"(?:\\.|[^\\\n])*?"'
    number_pattern: str = r"-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?\b"
    colon_pattern: str = r":"
    comma_pattern: str = r","
    null_pattern: str = r"\bnull\b"
    true_pattern: str = r"\btrue\b"
    false_pattern: str = r"\bfalse\b"

    object_entry_parser: Parser = field(init=False)
    array_element_parser: Parser = field(init=False)
    recursive_parser: Parser = field(init=False)

    quote_helper: QuoteHelper = field(default_factory=JsonQuoteHelper)

    def __post_init__(self):
        self.object_entry_parser = self.parse_object_entry
        self.array_element_parser = self
        self.recursive_parser = self

    def __call__(self, stream: TokenStream) -> AstJson:
        with stream.syntax(
            curly=self.curly_pattern,
            bracket=self.bracket_pattern,
            string=self.string_pattern,
            number=self.number_pattern,
            colon=self.colon_pattern,
            comma=self.comma_pattern,
            null=self.null_pattern,
            true=self.true_pattern,
            false=self.false_pattern,
        ):
            curly, bracket, string, number, null, true, false = stream.expect(
                ("curly", "{"),
                ("bracket", "["),
                "string",
                "number",
                "null",
                "true",
                "false",
            )

            if curly:
                entries: List[AstJsonObjectEntry] = []

                for _ in stream.peek_until(("curly", "}")):
                    entries.append(self.object_entry_parser(stream))

                    if not stream.get("comma"):
                        stream.expect(("curly", "}"))
                        break

                node = AstJsonObject(entries=AstChildren(entries))
                return set_location(node, curly, stream.current)

            elif bracket:
                elements: List[AstJson] = []

                for _ in stream.peek_until(("bracket", "]")):
                    elements.append(self.array_element_parser(stream))

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

    def parse_object_entry(self, stream: TokenStream) -> AstJsonObjectEntry:
        """Parse json object entry."""
        key = stream.expect("string")
        key_node = AstJsonObjectKey(value=self.quote_helper.unquote_string(key))
        key_node = set_location(key_node, key)

        stream.expect("colon")

        value_node = self.recursive_parser(stream)

        entry_node = AstJsonObjectEntry(key=key_node, value=value_node)
        return set_location(entry_node, key_node, value_node)


@dataclass
class JsonObjectParser(TypeConstraint):
    """Parser for json objects."""

    parser: Parser = field(default_factory=JsonParser)
    type: Type[AstJsonObject] = AstJsonObject
    message: str = "Expected json object."


@dataclass
class NbtParser:
    """Parser for nbt tags."""

    array_pattern: str = r"\[[BIL];"
    curly_pattern: str = r"\{|\}"
    bracket_pattern: str = r"\[|\]"
    quoted_string_pattern: str = r'"(?:\\.|[^\\\n])*?"' "|" r"'(?:\\.|[^\\\n])*?'"
    number_pattern: str = r"[+-]?(?:[0-9]*?\.[0-9]+|[0-9]+\.[0-9]*?|[1-9][0-9]*|0)(?:[eE][+-]?[0-9]+)?[bslfdBSLFD]?\b"
    string_pattern: str = r"[a-zA-Z0-9._+-]+"
    colon_pattern: str = r":"
    comma_pattern: str = r","

    compound_entry_parser: Parser = field(init=False)
    list_or_array_element_parser: Parser = field(init=False)
    recursive_parser: Parser = field(init=False)

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

    def __post_init__(self):
        self.compound_entry_parser = self.parse_compound_entry
        self.list_or_array_element_parser = self
        self.recursive_parser = self

    def __call__(self, stream: TokenStream) -> AstNbt:
        with stream.syntax(
            array=self.array_pattern,
            curly=self.curly_pattern,
            bracket=self.bracket_pattern,
            quoted_string=self.quoted_string_pattern,
            number=self.number_pattern,
            string=self.string_pattern,
            colon=self.colon_pattern,
            comma=self.comma_pattern,
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

                for _ in stream.peek_until(("curly", "}")):
                    entries.append(self.compound_entry_parser(stream))

                    if not stream.get("comma"):
                        stream.expect(("curly", "}"))
                        break

                node = AstNbtCompound(entries=AstChildren(entries))
                return set_location(node, curly, stream.current)

            elif bracket or array:
                elements: List[AstNbt] = []

                for _ in stream.peek_until(("bracket", "]")):
                    elements.append(self.list_or_array_element_parser(stream))

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
                    element_type = None
                    msg = "Expected all elements to have the same type."

                node = set_location(node, bracket or array, stream.current)

                for element in node.elements:
                    if isinstance(element, AstNbtValue):
                        if not element_type:
                            element_type = type(element.value)
                        elif type(element.value) is not element_type:
                            raise element.emit_error(InvalidSyntax(msg))
                    elif isinstance(element, AstNbt):  # type: ignore
                        if not element_type:
                            element_type = type(element)
                        elif type(element) is not element_type:
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

    def parse_compound_entry(self, stream: TokenStream) -> AstNbtCompoundEntry:
        """Parse nbt compound entry."""
        key = stream.expect_any("number", "string", "quoted_string")
        key_node = AstNbtCompoundKey(value=self.quote_helper.unquote_string(key))
        key_node = set_location(key_node, key)

        stream.expect("colon")

        value_node = self.recursive_parser(stream)

        entry_node = AstNbtCompoundEntry(key=key_node, value=value_node)
        return set_location(entry_node, key_node, value_node)


@dataclass
class NbtCompoundParser(TypeConstraint):
    """Parser for nbt compounds."""

    parser: Parser = field(default_factory=NbtParser)
    type: Type[AstNbtCompound] = AstNbtCompound
    message: str = "Expected nbt compound."


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
        if isinstance(node := self.parser(stream), AstResourceLocation):
            if node.is_tag:
                exc = InvalidSyntax(
                    f"Specifying a tag is not allowed {node.get_value()!r}."
                )
                raise node.emit_error(exc)

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
    data_tags_parser: Parser

    def __call__(self, stream: TokenStream) -> AstBlock:
        identifier = self.resource_location_parser(stream)

        location = identifier.location
        end_location = identifier.end_location

        if block_states := self.block_states_parser(stream):
            end_location = stream.current.end_location
        else:
            block_states = AstChildren[AstBlockState]()

        data_tags = self.data_tags_parser(stream)

        node = AstBlock(
            identifier=identifier,
            block_states=block_states,
            data_tags=data_tags,
        )
        return set_location(node, location, data_tags if data_tags else end_location)


@dataclass
class BlockStatesParser:
    """Parser for minecraft block state."""

    key_parser: Parser
    value_parser: Parser

    def __call__(self, stream: TokenStream) -> AstChildren[AstBlockState]:
        block_states: List[AstBlockState] = []

        with stream.syntax(
            bracket=r"\[|\]",
            equal=r"=",
            comma=r",",
        ):
            stream.expect(("bracket", "["))

            for _ in stream.peek_until(("bracket", "]")):
                key_node = self.key_parser(stream)
                stream.expect("equal")
                value_node = self.value_parser(stream)

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
    data_tags_parser: Parser

    def __call__(self, stream: TokenStream) -> AstItem:
        identifier = self.resource_location_parser(stream)
        location = identifier.location
        end_location = identifier.end_location

        data_tags = self.data_tags_parser(stream)

        node = AstItem(identifier=identifier, data_tags=data_tags)
        return set_location(node, location, data_tags if data_tags else end_location)


@dataclass
class NoBlockStatesConstraint:
    """Constraint that disallows block states."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        if isinstance(node := self.parser(stream), AstBlock):
            if node.block_states:
                exc = InvalidSyntax("Specifying block states not allowed.")
                raise node.emit_error(exc)
        return node


@dataclass
class NoDataTagsConstraint:
    """Constraint that disallows data tags."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        if isinstance(node := self.parser(stream), AstBlock):
            if node.data_tags:
                exc = InvalidSyntax("Specifying data tags not allowed.")
                raise node.emit_error(exc)
        return node


@dataclass
class BasicLiteralParser:
    """Parser for simple literal values."""

    type: Type[AstLiteral]

    def __call__(self, stream: TokenStream) -> Any:
        if not self.type.parser:
            raise ValueError(
                f"Literal node type must have an associated parser {self.type!r}."
            )
        with stream.syntax(**{self.type.parser: self.type.regex.pattern}):
            token = stream.expect(self.type.parser)
        node = self.type(value=token.value)
        return set_location(node, token)


@dataclass
class RangeParser:
    """Parser for ranges."""

    pattern: str = rf"\.\.{NUMBER_PATTERN}|{NUMBER_PATTERN}\.\.(?:{NUMBER_PATTERN})?|{NUMBER_PATTERN}"

    def __call__(self, stream: TokenStream) -> AstRange:
        with stream.syntax(range=self.pattern):
            token = stream.expect("range")
            return set_location(AstRange.from_value(token.value), token)


@dataclass
class IntegerRangeConstraint:
    """Constraint that disallows decimal ranges."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        if isinstance(node := self.parser(stream), AstRange):
            if isinstance(node.min, float) or isinstance(node.max, float):
                raise node.emit_error(InvalidSyntax("Expected integer range."))
        return node


@dataclass
class LengthConstraint:
    """Constraint that only allows up to a limited number of characters."""

    parser: Parser
    limit: int

    def __call__(self, stream: TokenStream) -> Any:
        if isinstance(node := self.parser(stream), AstLiteral):
            if len(node.value) > self.limit:
                exc = InvalidSyntax(f"Expected up to {self.limit} characters.")
                raise node.emit_error(exc)
        return node


@dataclass
class TimeParser(NumericParser):
    """Parser for time."""

    name: str = "time"
    pattern: str = NUMBER_PATTERN + r"[dst]?"

    def create_node(self, stream: TokenStream) -> Any:
        return set_location(AstTime.from_value(stream.current.value), stream.current)


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

    key_parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        with stream.syntax(
            equal=r"=",
            exclamation=r"!",
        ):
            key_node = self.key_parser(stream)
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
        if isinstance(node := self.parser(stream), AstSelectorArgument):
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
        if isinstance(node := self.parser(stream), AstSelectorArgument):
            if not node.value and node.key.value not in self.allow_no_value:
                exc = InvalidSyntax(f"Argument {node.key.value!r} must have a value.")
                raise node.emit_error(exc)
        return node


def parse_selector_scores(stream: TokenStream) -> AstSelectorScores:
    """Parse selector scores."""
    with stream.syntax(
        curly=r"\{|\}",
        objective=AstObjective.regex.pattern,
        equal=r"=",
        comma=r",",
    ):
        curly = stream.expect(("curly", "{"))

        scores: List[AstSelectorScoreMatch] = []

        for _ in stream.peek_until(("curly", "}")):
            key_node = delegate("objective", stream)
            stream.expect("equal")

            value_node = delegate("integer_range", stream)

            match_node = AstSelectorScoreMatch(key=key_node, value=value_node)
            scores.append(set_location(match_node, key_node, value_node))

            if not stream.get("comma"):
                stream.expect(("curly", "}"))
                break

        node = AstSelectorScores(scores=AstChildren(scores))
        return set_location(node, curly, stream.current)


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
                    pkey = delegate("advancement_predicate", stream)
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
        node = self.parser(stream)

        if not isinstance(node, AstSelector):
            return node

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
        node = self.parser(stream)

        if not isinstance(node, AstSelector):
            return node

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
        with stream.syntax(literal=AstLiteral.regex.pattern):
            hint = stream.peek()

        if hint:
            if hint.value.startswith("@"):
                return self.selector_parser(stream)

            if hint.value.count("-") == 4:
                with stream.alternative():
                    return delegate("uuid", stream)

        return delegate("player_name", stream)


def parse_wildcard(stream: TokenStream) -> AstWildcard:
    """Parse wildcard."""
    with stream.syntax(wildcard=r"\*"):
        token = stream.expect("wildcard")
        return set_location(AstWildcard(), token)


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
                text_node = AstMessageText(value=text.value)
                text_node = set_location(text_node, text)
                fragments.append(text_node)

            with stream.syntax(text=None):
                if consume_line_continuation(stream):
                    whitespace_node = AstMessageText(value=" ")
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
    """Parser for nbt paths."""

    integer_parser: Parser = field(
        default_factory=lambda: IntegerConstraint(NumericParser())
    )
    nbt_compound_parser: Parser = field(default_factory=NbtCompoundParser)

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
                    component_node = AstNbtPathKey(
                        value=self.quote_helper.unquote_string(quoted_string),
                    )
                    components.append(set_location(component_node, quoted_string))
                elif string:
                    component_node = AstNbtPathKey(value=string.value)
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
            yield self.nbt_compound_parser(stream)
            return

        while bracket := stream.get(("bracket", "[")):
            index = None

            hint = stream.peek()
            if hint and hint.match(("curly", "{")):
                index = self.nbt_compound_parser(stream)
            elif hint and not hint.match(("bracket", "]")):
                index = self.integer_parser(stream)

            close_bracket = stream.expect(("bracket", "]"))

            subscript_node = AstNbtPathSubscript(index=index)
            yield set_location(subscript_node, bracket, close_bracket)


def parse_particle(stream: TokenStream) -> AstParticle:
    """Parse particle."""
    parameters = None

    if isinstance(name := delegate("resource_location", stream), AstResourceLocation):
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
class AlternativeParser:
    """Parser that tries the given alternatives in order."""

    parsers: List[Parser]

    def __call__(self, stream: TokenStream) -> Any:
        for parser, alternative in stream.choose(*self.parsers):
            with alternative:
                return parser(stream)
