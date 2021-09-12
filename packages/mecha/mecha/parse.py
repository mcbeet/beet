__all__ = [
    "get_default_parsers",
    "get_stream_spec",
    "get_stream_scope",
    "get_stream_properties",
    "delegate",
    "QuoteHelper",
    "parse_root",
    "parse_command",
    "parse_argument",
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
    "NbtParser",
    "NbtCompoundConstraint",
    "AdjacentConstraint",
    "ResourceLocationParser",
    "NoTagConstraint",
    "BlockParser",
    "ItemParser",
    "NoBlockStatesConstraint",
    "NoDataTagsConstraint",
    "ValueParser",
    "ValueConstraint",
    "RangeParser",
    "LengthConstraint",
    "parse_swizzle",
    "TimeParser",
    "parse_uuid",
    "SelectorParser",
    "SelectorArgumentParser",
    "SelectorArgumentInvertConstraint",
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
    "NUMBER_PATTERN",
]


import re
from dataclasses import dataclass, field
from functools import partial
from typing import Any, Dict, Iterator, List, Literal, Optional, Tuple, Type, overload
from uuid import UUID

# pyright: reportMissingTypeStubs=false
from nbtlib import Byte, Double, Float, Int, Long, OutOfRange, Short, String
from tokenstream import InvalidSyntax, SourceLocation, Token, TokenStream, set_location

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
from .spec import CommandSpec, Parser

NUMBER_PATTERN: str = r"-?(?:\d+\.?\d*|\.\d+)"


# TODO: Handle the extended syntax by default and validate vanilla compatibility in a separate pass


def get_default_parsers() -> Dict[str, Parser]:
    """Return the default parsers."""
    return {
        ################################################################################
        # Primitives
        ################################################################################
        "literal": ValueParser(name="literal"),
        "bool": parse_bool,
        "numeric": NumericParser(),
        "integer": IntegerConstraint(delegate("numeric")),
        "coordinate": CoordinateParser(),
        "integer_coordinate": IntegerConstraint(delegate("coordinate")),
        "time": TimeParser(),
        "word": StringParser(type="word"),
        "phrase": StringParser(type="phrase"),
        "greedy": StringParser(type="greedy"),
        "json": JsonParser(),
        "nbt": NbtParser(),
        "nbt_compound": NbtCompoundConstraint(delegate("nbt")),
        "adjacent_nbt_compound": AdjacentConstraint(
            parser=delegate("nbt_compound"),
            hint=r"\{",
        ),
        "nbt_path": NbtPathParser(),
        "range": RangeParser(type=float),
        "integer_range": RangeParser(type=int),
        "resource_location_or_tag": ResourceLocationParser(),
        "resource_location": NoTagConstraint(delegate("resource_location_or_tag")),
        "uuid": parse_uuid,
        "objective": LengthConstraint(
            parser=ValueParser("objective", r"[a-zA-Z0-9_.+-]+|\*"),
            limit=16,
        ),
        "player_name": LengthConstraint(
            parser=ValueParser("player_name", r"[a-zA-Z0-9_.+-]+"),
            limit=16,
        ),
        "swizzle": parse_swizzle,
        "team": ValueParser("team", r"[a-zA-Z0-9_.+-]+"),
        ################################################################################
        # Selector
        ################################################################################
        "selector": SelectorParser(),
        "selector:argument": SelectorArgumentInvertConstraint(
            SelectorArgumentParser(),
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
        "selector:argument:sort": ValueConstraint(
            parser=delegate("word"),
            values=[
                "nearest",
                "furthest",
                "random",
                "arbitrary",
            ],
        ),
        "selector:argument:level": delegate("integer_range"),
        "selector:argument:gamemode": ValueConstraint(
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
        "command:argument:minecraft:block_predicate": BlockParser(
            resource_location_parser=delegate("resource_location_or_tag"),
        ),
        "command:argument:minecraft:block_state": BlockParser(
            resource_location_parser=delegate("resource_location"),
        ),
        "command:argument:minecraft:color": ValueConstraint(
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
        "command:argument:minecraft:entity_anchor": ValueConstraint(
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
        "command:argument:minecraft:item_predicate": ItemParser(
            resource_location_parser=delegate("resource_location_or_tag"),
        ),
        "command:argument:minecraft:item_slot": delegate("word"),
        "command:argument:minecraft:item_stack": ItemParser(
            resource_location_parser=delegate("resource_location"),
        ),
        "command:argument:minecraft:message": parse_message,
        "command:argument:minecraft:mob_effect": delegate("resource_location"),
        "command:argument:minecraft:nbt_compound_tag": delegate("nbt_compound"),
        "command:argument:minecraft:nbt_path": delegate("nbt_path"),
        "command:argument:minecraft:nbt_tag": delegate("nbt"),
        "command:argument:minecraft:objective": delegate("objective"),
        "command:argument:minecraft:objective_criteria": delegate("resource_location"),
        "command:argument:minecraft:operation": ValueConstraint(
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
        # TODO: "minecraft:particle"
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


def get_stream_spec(stream: TokenStream) -> CommandSpec:
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
class QuoteHelper:
    """Helper for removing quotes and interpreting escape sequences."""

    escape_regex: "re.Pattern[str]" = field(default_factory=lambda: re.compile(r"\\."))
    escape_sequences: Dict[str, str] = field(default_factory=dict)

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


def parse_root(stream: TokenStream) -> AstRoot:
    """Parse root."""
    with stream.syntax(comment=r"#.+$", literal=r"\S+"), stream.intercept("newline"):
        start = stream.peek()

        if not start:
            node = AstRoot(filename=None, commands=AstChildren())
            return set_location(node, SourceLocation(0, 1, 1))

        commands: List[AstCommand] = []

        for _ in stream.peek_until():
            while stream.get("newline", "comment"):
                continue
            if stream.peek():
                commands.append(delegate("command", stream))

        node = AstRoot(filename=None, commands=AstChildren(commands))
        return set_location(node, start, stream.current)


def parse_command(stream: TokenStream) -> AstCommand:
    """Parse command."""
    spec = get_stream_spec(stream)
    scope = get_stream_scope(stream)
    tree = spec.tree.get(scope)

    arguments: List[AstNode] = []

    with stream.checkpoint():
        location = stream.expect().location
        end_location = location

    while tree and tree.children:
        for (name, child), alternative in stream.choose(*tree.children.items()):
            with alternative, stream.provide(scope=scope + (name,)):
                if child.type == "literal":
                    token = stream.expect(("literal", name))
                    end_location = token.end_location

                elif child.type == "argument":
                    node = delegate("command:argument", stream)
                    arguments.append(node)
                    end_location = node.end_location

                scope = stream.data["scope"]
                tree = child

        if tree.executable and stream.get("newline"):
            break

        target = spec.tree.get(tree.redirect)
        recursive = target and target.subcommand

        if tree.subcommand or recursive:
            subcommand_scope = tree.redirect if tree.redirect is not None else scope
            with stream.provide(scope=subcommand_scope):
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


def parse_bool(stream: TokenStream) -> AstValue[bool]:
    """Parse bool."""
    with stream.syntax(literal=r"\w+"):
        token = stream.expect_any(("literal", "true"), ("literal", "false"))
    node = AstValue[bool](value=token.value == "true")
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
        node = AstValue[float](
            value=float(token.value) if "." in token.value else int(token.value),
        )
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

        value = float(value) if "." in value else int(value)

        node = AstCoordinate(type=coordinate_type, value=value)
        return set_location(node, token)


@dataclass
class IntegerConstraint:
    """Constraint that disallows decimal numeric values."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        node: AstValue[Any] = self.parser(stream)

        if not isinstance(node.value, int):
            raise node.emit_error(InvalidSyntax("Expected integer value."))

        return node


@dataclass
class MinMaxConstraint:
    """Constraint that checks that the value conforms to the min and max properties."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        properties = get_stream_properties(stream)
        node: AstValue[float] = self.parser(stream)

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

    def __call__(self, stream: TokenStream) -> AstValue[str]:
        if self.type == "greedy":
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
                if self.type == "word":
                    token = stream.expect("word")
                else:
                    token = stream.expect_any("word", "quoted_string")

        node = AstValue[str](value=self.quote_helper.unquote_string(token))
        return set_location(node, token)


def parse_string_argument(stream: TokenStream) -> AstValue[str]:
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
        default_factory=lambda: QuoteHelper(
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
                    key_node = AstValue[str](
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
                value = float(number.value)

            node = AstJsonValue(value=value)  # type: ignore
            return set_location(node, stream.current)


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
            curly=r"\{|\}",
            bracket=r"\[|\]",
            quoted_string=r'"(?:\\.|[^\\\n])*?"' "|" r"'(?:\\.|[^\\\n])*?'",
            number=r"[+-]?(?:[0-9]*?\.[0-9]+|[0-9]+\.[0-9]*?|[1-9][0-9]*|0)(?:[eE][+-]?[0-9]+)?[bslfdBSLFD]?\b",
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
                    key_node = AstValue[str](
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

            elif bracket:
                elements: List[AstNbt] = []

                for _ in stream.peek_until(("bracket", "]")):
                    elements.append(self(stream))

                    if not stream.get("comma"):
                        stream.expect(("bracket", "]"))
                        break

                node = AstNbtList(elements=AstChildren(elements))
                return set_location(node, bracket, stream.current)

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

            # TODO: Arrays

            node = AstNbtValue(value=value)  # type: ignore
            return set_location(node, stream.current)


@dataclass
class NbtCompoundConstraint:
    """Constraint that only allows nbt compound tags."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        node = self.parser(stream)

        if not isinstance(node, AstNbtCompound):
            raise node.emit_error(InvalidSyntax("Expected nbt compound."))

        return node


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

            if namespace:
                namespace_node = AstValue[str](value=namespace)
                namespace_node = set_location(
                    namespace_node,
                    location,
                    location.with_horizontal_offset(len(namespace)),
                )
                location = namespace_node.end_location.with_horizontal_offset(1)
            else:
                namespace_node = None

            path_node = AstValue[str](value=path)
            path_node = set_location(path_node, location, token)

            node = AstResourceLocation(
                is_tag=is_tag,
                namespace=namespace_node,
                path=path_node,
            )
            return set_location(node, token)


@dataclass
class NoTagConstraint:
    """Constraint that disallows resource locations refering to tags."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        node: AstResourceLocation = self.parser(stream)

        if node.is_tag:
            raise node.emit_error(InvalidSyntax("Specifying a tag is not allowed."))

        return node


@dataclass
class BlockParser:
    """Parser for minecraft blocks."""

    resource_location_parser: Parser

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

            for key in stream.collect("state"):
                key_node = AstValue[str](value=key.value)
                key_node = set_location(key_node, key)

                stream.expect("equal")

                value = stream.expect("state")
                value_node = AstValue[str](value=value.value)
                value_node = set_location(value_node, value)

                entry_node = AstBlockState(key=key_node, value=value_node)
                entry_node = set_location(entry_node, key_node, value_node)
                block_states.append(entry_node)

                if not stream.get("comma"):
                    break

            close_bracket = stream.expect(("bracket", "]"))
            end_location = close_bracket.end_location

        data_tags = delegate("adjacent_nbt_compound", stream)

        node = AstBlock(
            identifier=identifier,
            block_states=AstChildren(block_states),
            data_tags=data_tags,
        )
        return set_location(node, location, data_tags if data_tags else end_location)


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
class ValueParser:
    """Parser for simple string values."""

    name: str
    pattern: str = r"\S+"

    def __call__(self, stream: TokenStream) -> AstValue[str]:
        with stream.syntax(**{self.name: self.pattern}):
            token = stream.expect(self.name)
        node = AstValue[str](value=token.value)
        return set_location(node, token)


@dataclass
class ValueConstraint:
    """Constraint that only allows a set of predefined values."""

    parser: Parser
    values: List[Any]

    def __call__(self, stream: TokenStream) -> Any:
        node: AstValue[str] = self.parser(stream)

        if node.value not in self.values:
            raise node.emit_error(InvalidSyntax(f"Unexpected value {node.value!r}."))

        return node


@dataclass
class RangeParser:
    """Parser for ranges."""

    type: Type[Any]
    pattern: str = fr"\.\.{NUMBER_PATTERN}|{NUMBER_PATTERN}\.\.(?:{NUMBER_PATTERN})?|{NUMBER_PATTERN}"

    def __call__(self, stream: TokenStream) -> AstRange:
        with stream.syntax(range=self.pattern):
            token = stream.expect("range")
            minimum, separator, maximum = token.value.partition("..")

            if not separator:
                maximum = minimum

            if issubclass(self.type, int) and ("." in minimum or "." in maximum):
                raise token.emit_error(InvalidSyntax("Expected integer range."))

            node = AstRange(
                min=self.type(minimum) if minimum else None,
                max=self.type(maximum) if maximum else None,
            )
            return set_location(node, token)


@dataclass
class LengthConstraint:
    """Constraint that only allows up to a limited number of characters."""

    parser: Parser
    limit: int

    def __call__(self, stream: TokenStream) -> Any:
        node: AstValue[str] = self.parser(stream)

        if len(node.value) > self.limit:
            exc = InvalidSyntax(f"Expected up to {self.limit} characters.")
            raise node.emit_error(exc)

        return node


def parse_swizzle(stream: TokenStream) -> AstValue[str]:
    """Parse swizzle."""
    node = delegate("literal", stream)

    normalized = set(node.value[:3]) & {"x", "y", "z"}
    if not normalized or len(node.value) != len(normalized):
        raise node.emit_error(InvalidSyntax(f"Invalid swizzle {node.value!r}."))

    return node


@dataclass
class TimeParser(NumericParser):
    """Parser for time."""

    type: Type[float] = float
    name: str = "time"
    pattern: str = NUMBER_PATTERN + r"[dst]?"

    def create_node(self, stream: TokenStream) -> Any:
        token = stream.current
        value = token.value

        if value.endswith(("d", "s", "t")):
            suffix = value[-1]
            value = value[:-1]
        else:
            suffix = None

        node = AstTime(value=self.type(value), suffix=suffix)  # type: ignore
        return set_location(node, token)


def parse_uuid(stream: TokenStream) -> AstValue[UUID]:
    """Parse uuid."""
    with stream.syntax(uuid="-".join([r"[a-fA-F0-9]+"] * 5)):
        token = stream.expect("uuid")
    node = AstValue[UUID](value=UUID(token.value))
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
            argument=r"[a-z_]+",
            equal=r"=",
            exclamation=r"!",
        ):
            key = stream.expect("argument")
            key_node = AstValue[str](value=key.value)
            key_node = set_location(key_node, key)

            stream.expect("equal")

            inverted = stream.get("exclamation") is not None

            try:
                value_node = delegate(f"selector:argument:{key.value}", stream)
            except UnrecognizedParser as exc:
                if not exc.parser.startswith("selector:argument:"):
                    raise
                syntax_exc = InvalidSyntax(f"Invalid selector argument {key.value!r}.")
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
            key_node = AstValue[str](value=key.value)
            key_node = set_location(key_node, key)

            stream.expect("equal")

            value_node = delegate("minecraft:integer_range", stream)

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
            key_node = delegate("minecraft:resource_location", stream)
            stream.expect("equal")
            value_node = delegate("brigadier:bool", stream)

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
                is_player = not argument.inverted and argument.value in [
                    AstResourceLocation(
                        namespace=AstValue[str](value="minecraft"),
                        path=AstValue[str](value="player"),
                    ),
                    AstResourceLocation(
                        path=AstValue[str](value="player"),
                    ),
                ]

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
                is_single = arg.value == AstValue[int](value=1)

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
                node = AstValue[str](value=token.value)
                return set_location(node, token)
        return self.entity_parser(stream)


def parse_message(stream: TokenStream) -> AstMessage:
    """Parse message."""
    with stream.intercept("whitespace"):
        while stream.get("whitespace"):
            continue

    with stream.syntax(selector=r"@[praes]", literal=r"\S+"):
        words: List[Any] = []

        for selector, literal in stream.collect("selector", "literal"):
            if selector:
                stream.index -= 1
                words.append(delegate("selector", stream))
            elif literal:
                word_node = AstValue[str](value=literal.value)
                word_node = set_location(word_node, literal)
                words.append(word_node)

    if not words:
        raise stream.emit_error(InvalidSyntax("Empty message not allowed."))

    node = AstMessage(words=AstChildren(words))
    return set_location(node, words[0], words[-1])


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
                    component_node = AstValue[str](
                        value=self.quote_helper.unquote_string(quoted_string),
                    )
                    components.append(set_location(component_node, quoted_string))
                elif string:
                    component_node = AstValue[str](value=string.value)
                    components.append(set_location(component_node, string))

                components.extend(self.parse_modifiers(stream))

        if not components:
            raise stream.emit_error(InvalidSyntax("Empty nbt path not allowed."))

        node = AstNbtPath(
            components=AstChildren(components),
        )
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
