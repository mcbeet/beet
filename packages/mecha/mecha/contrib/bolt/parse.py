__all__ = [
    "get_bolt_parsers",
    "get_stream_identifiers",
    "get_stream_pending_identifiers",
    "UndefinedIdentifier",
    "create_bolt_root_parser",
    "ExecuteIfConditionConstraint",
    "InterpolationParser",
    "parse_statement",
    "AssignmentTargetParser",
    "IfElseLoweringParser",
    "BreakContinueConstraint",
    "FlushPendingIdentifiersParser",
    "parse_function_signature",
    "parse_function_root",
    "parse_del_target",
    "parse_identifier",
    "ImportLocationConstraint",
    "ImportStatementHandler",
    "parse_import_name",
    "FunctionRootBacktracker",
    "ReturnConstraint",
    "YieldConstraint",
    "BinaryParser",
    "UnaryParser",
    "UnpackParser",
    "UnpackConstraint",
    "KeywordParser",
    "LookupParser",
    "PrimaryParser",
    "parse_dict_item",
    "LiteralParser",
]


import keyword
import re
from dataclasses import dataclass, field, replace
from difflib import get_close_matches
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, cast

from beet.core.utils import required_field
from tokenstream import InvalidSyntax, Token, TokenStream, UnexpectedToken, set_location

from mecha import (
    AlternativeParser,
    AstChildren,
    AstCommand,
    AstResourceLocation,
    AstRoot,
    CompilationDatabase,
    Parser,
    consume_line_continuation,
    delegate,
    get_stream_scope,
)
from mecha.contrib.relative_location import resolve_using_database
from mecha.utils import (
    JsonQuoteHelper,
    QuoteHelper,
    normalize_whitespace,
    string_to_number,
)

from .ast import (
    AstAssignment,
    AstAttribute,
    AstCall,
    AstDict,
    AstDictItem,
    AstExpression,
    AstExpressionBinary,
    AstExpressionUnary,
    AstFormatString,
    AstFunctionRoot,
    AstFunctionSignature,
    AstFunctionSignatureArgument,
    AstIdentifier,
    AstImportedIdentifier,
    AstInterpolation,
    AstKeyword,
    AstList,
    AstLookup,
    AstSlice,
    AstTarget,
    AstTargetAttribute,
    AstTargetUnpack,
    AstTargetIdentifier,
    AstTargetItem,
    AstTuple,
    AstUnpack,
    AstValue,
)

KEYWORD_PATTERN: str = "|".join(rf"\b{kw}\b" for kw in keyword.kwlist)

TRUE_PATTERN: str = r"\b[tT]rue\b"
FALSE_PATTERN: str = r"\b[fF]alse\b"
NULL_PATTERN: str = r"\b(?:null|None)\b"
IDENTIFIER_PATTERN: str = rf"(?!_mecha_|{KEYWORD_PATTERN})[a-zA-Z_][a-zA-Z0-9_]*\b"
STRING_PATTERN: str = r'"(?:\\.|[^\\\n])*?"' "|" r"'(?:\\.|[^\\\n])*?'"
NUMBER_PATTERN: str = r"(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?\b"
RESOURCE_LOCATION_PATTERN: str = r"(?:\.\./|\./|[0-9a-z_\-\.]+:)[0-9a-z_./-]+"

IMPORT_REGEX = re.compile(rf"^{IDENTIFIER_PATTERN}(?:\.{IDENTIFIER_PATTERN})*$")


def get_bolt_parsers(
    parsers: Dict[str, Parser],
    database: CompilationDatabase,
) -> Dict[str, Parser]:
    """Return the bolt parsers."""
    return {
        ################################################################################
        # Command
        ################################################################################
        "root": create_bolt_root_parser(parsers["root"]),
        "nested_root": create_bolt_root_parser(parsers["nested_root"]),
        "command": ImportStatementHandler(
            ExecuteIfConditionConstraint(parsers["command"])
        ),
        "command:argument:bolt:statement": delegate("bolt:statement"),
        "command:argument:bolt:assignment_target": delegate("bolt:assignment_target"),
        "command:argument:bolt:import": delegate("bolt:import"),
        "command:argument:bolt:import_name": delegate("bolt:import_name"),
        "command:argument:bolt:expression": delegate("bolt:expression"),
        "command:argument:bolt:function_signature": delegate("bolt:function_signature"),
        "command:argument:bolt:function_root": delegate("bolt:function_root"),
        "command:argument:bolt:del_target": delegate("bolt:del_target"),
        ################################################################################
        # Bolt
        ################################################################################
        "bolt:statement": parse_statement,
        "bolt:assignment_target": AssignmentTargetParser(
            allow_undefined_identifiers=True,
            allow_multiple=True,
        ),
        "bolt:augmented_assignment_target": AssignmentTargetParser(),
        "bolt:function_signature": parse_function_signature,
        "bolt:function_root": parse_function_root,
        "bolt:del_target": parse_del_target,
        "bolt:interpolation": PrimaryParser(delegate("bolt:identifier")),
        "bolt:identifier": parse_identifier,
        "bolt:import": ImportLocationConstraint(parsers["resource_location_or_tag"]),
        "bolt:import_name": parse_import_name,
        "bolt:expression": delegate("bolt:disjunction"),
        "bolt:disjunction": BinaryParser(
            operators=[r"\bor\b"],
            parser=delegate("bolt:conjunction"),
        ),
        "bolt:conjunction": BinaryParser(
            operators=[r"\band\b"],
            parser=delegate("bolt:inversion"),
        ),
        "bolt:inversion": UnaryParser(
            operators=[r"\bnot\b"],
            parser=delegate("bolt:comparison"),
        ),
        "bolt:comparison": BinaryParser(
            operators=[
                "==",
                "!=",
                "<=",
                "<",
                ">=",
                ">",
                r"\bnot\s+in\b",
                r"\bin\b",
                r"\bis\s+not\b",
                r"\bis\b",
            ],
            parser=delegate("bolt:bitwise_or"),
        ),
        "bolt:bitwise_or": BinaryParser(
            operators=[r"\|(?!=)"],
            parser=delegate("bolt:bitwise_xor"),
        ),
        "bolt:bitwise_xor": BinaryParser(
            operators=[r"\^(?!=)"],
            parser=delegate("bolt:bitwise_and"),
        ),
        "bolt:bitwise_and": BinaryParser(
            operators=[r"&(?!=)"],
            parser=delegate("bolt:shift_expr"),
        ),
        "bolt:shift_expr": BinaryParser(
            operators=[r"<<(?!=)", r">>(?!=)"],
            parser=delegate("bolt:sum"),
        ),
        "bolt:sum": BinaryParser(
            operators=[r"\+(?!=)", r"-(?!=)"],
            parser=delegate("bolt:term"),
        ),
        "bolt:term": BinaryParser(
            operators=[r"\*(?!=)", r"//(?!=)", r"/(?!=)", r"%(?!=)"],
            parser=delegate("bolt:factor"),
        ),
        "bolt:factor": UnaryParser(
            operators=[r"\+", "-"],
            parser=delegate("bolt:power"),
        ),
        "bolt:power": BinaryParser(
            operators=[r"\*\*(?!=)"],
            parser=delegate("bolt:primary"),
            right_associative=True,
        ),
        "bolt:lookup_argument": LookupParser(delegate("bolt:expression")),
        "bolt:call_argument": AlternativeParser(
            [
                KeywordParser(delegate("bolt:expression")),
                UnpackParser(delegate("bolt:expression")),
                delegate("bolt:expression"),
            ]
        ),
        "bolt:primary": PrimaryParser(delegate("bolt:atom")),
        "bolt:atom": AlternativeParser(
            [
                delegate("bolt:identifier"),
                delegate("bolt:literal"),
            ]
        ),
        "bolt:list_item": AlternativeParser(
            [
                UnpackConstraint(
                    type="list",
                    parser=UnpackParser(delegate("bolt:expression")),
                ),
                delegate("bolt:expression"),
            ]
        ),
        "bolt:dict_item": AlternativeParser(
            [
                UnpackConstraint(
                    type="dict",
                    parser=UnpackParser(delegate("bolt:expression")),
                ),
                parse_dict_item,
            ]
        ),
        "bolt:literal": LiteralParser(database),
        ################################################################################
        # Interpolation
        ################################################################################
        "bool": InterpolationParser("bool", parsers["bool"], fallback=True),
        "numeric": InterpolationParser(
            "numeric", parsers["numeric"], prefix="-", fallback=True
        ),
        "coordinate": InterpolationParser(
            "coordinate", parsers["coordinate"], prefix="[~^]-?|-", fallback=True
        ),
        "time": InterpolationParser("time", parsers["time"], fallback=True),
        "word": InterpolationParser("word", parsers["word"]),
        "phrase": InterpolationParser("phrase", parsers["phrase"]),
        "greedy": InterpolationParser("greedy", parsers["greedy"]),
        "json": InterpolationParser("json", parsers["json"]),
        "nbt": InterpolationParser("nbt", parsers["nbt"]),
        "nbt_path": InterpolationParser("nbt_path", parsers["nbt_path"]),
        "range": InterpolationParser("range", parsers["range"], fallback=True),
        "resource_location_or_tag": InterpolationParser(
            "resource_location", parsers["resource_location_or_tag"]
        ),
        "item_slot": InterpolationParser(
            "item_slot", parsers["item_slot"], fallback=True
        ),
        "objective": InterpolationParser("objective", parsers["objective"]),
        "objective_criteria": InterpolationParser(
            "objective_criteria", parsers["objective_criteria"]
        ),
        "scoreboard_slot": InterpolationParser(
            "scoreboard_slot", parsers["scoreboard_slot"], fallback=True
        ),
        "swizzle": InterpolationParser("swizzle", parsers["swizzle"], fallback=True),
        "team": InterpolationParser("team", parsers["team"]),
        "color": InterpolationParser("color", parsers["color"]),
        "sort_order": InterpolationParser("sort_order", parsers["sort_order"]),
        "gamemode": InterpolationParser("gamemode", parsers["gamemode"]),
        "message": InterpolationParser("message", parsers["message"]),
        "block_pos": InterpolationParser("vec3", parsers["block_pos"], fallback=True),
        "column_pos": InterpolationParser("vec2", parsers["column_pos"], fallback=True),
        "rotation": InterpolationParser("vec2", parsers["rotation"], fallback=True),
        "vec2": InterpolationParser("vec2", parsers["vec2"], fallback=True),
        "vec3": InterpolationParser("vec3", parsers["vec3"], fallback=True),
        "entity": InterpolationParser("entity", parsers["entity"]),
        "score_holder": InterpolationParser("entity", parsers["score_holder"]),
    }


def get_stream_identifiers(stream: TokenStream) -> Set[str]:
    """Return the set of accessible identifiers currently associated with the token stream."""
    return stream.data.setdefault("identifiers", set())


def get_stream_pending_identifiers(stream: TokenStream) -> Set[str]:
    """Return the set of pending identifiers currently associated with the token stream."""
    return stream.data.setdefault("pending_identifiers", set())


class UndefinedIdentifier(UnexpectedToken):
    """Raised when an identifier is not defined."""

    identifiers: Tuple[str, ...]

    def __init__(self, token: Token, identifiers: Iterable[str]):
        super().__init__(token)
        self.identifiers = tuple(identifiers)

    def __str__(self) -> str:
        msg = f"Identifier {self.token.value!r} is not defined."

        if matches := get_close_matches(self.token.value, self.identifiers):
            matches = [repr(m) for m in matches]

            if len(matches) == 1:
                suggestion = f"{matches[0]}"
            else:
                *head, before_last, last = matches
                suggestion = ", ".join(head + [f"{before_last} or {last}"])

            msg += f" Did you mean {suggestion}?"

        return msg


def create_bolt_root_parser(parser: Parser):
    """Return parser for the root node for bolt."""
    return FunctionRootBacktracker(
        FlushPendingIdentifiersParser(
            ReturnConstraint(
                YieldConstraint(
                    BreakContinueConstraint(
                        parser=IfElseLoweringParser(parser),
                        allowed_scopes={
                            ("while", "condition", "body"),
                            ("for", "target", "in", "iterable", "body"),
                        },
                    )
                )
            )
        )
    )


@dataclass
class ExecuteIfConditionConstraint:
    """Constraint that prevents inlining if conditions as execute subcommands."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        if isinstance(node := self.parser(stream), AstCommand):
            if node.identifier == "execute:if:condition:body":
                exc = InvalidSyntax("Can't inline conditions as execute subcommands.")
                raise set_location(exc, node)

        return node


@dataclass
class InterpolationParser:
    """Parser for interpolation."""

    converter: str
    parser: Parser
    prefix: Optional[str] = None
    fallback: bool = False

    def __call__(self, stream: TokenStream) -> Any:
        order = ["interpolation", "original"]
        if self.fallback:
            order.reverse()
        for parser, alternative in stream.choose(*order):
            with alternative:
                if parser == "interpolation":
                    with stream.syntax(prefix=self.prefix):
                        prefix = stream.get("prefix")
                    node = delegate("bolt:interpolation", stream)
                    node = AstInterpolation(
                        prefix=prefix.value if prefix else None,
                        converter=self.converter,
                        value=node,
                    )
                    return set_location(node, prefix or node.value, node.value)
                elif parser == "original":
                    return self.parser(stream)


def parse_statement(stream: TokenStream) -> Any:
    """Parse statement."""
    identifiers = get_stream_identifiers(stream)
    pending_identifiers = get_stream_pending_identifiers(stream)

    for parser, alternative in stream.choose(
        "bolt:augmented_assignment_target",
        "bolt:assignment_target",
        "bolt:expression",
    ):
        with alternative:
            pending_identifiers.clear()
            node = delegate(parser, stream)

            pattern = r"=(?!=)|\+=|-=|\*=|//=|/=|%=|&=|\|=|\^=|<<=|>>=|\*\*="

            if isinstance(node, AstTarget):
                if parser == "bolt:assignment_target":
                    pattern = r"=(?!=)"
                with stream.syntax(assignment=pattern):
                    op = stream.expect("assignment")

                expression = delegate("bolt:expression", stream)

                identifiers |= pending_identifiers
                pending_identifiers.clear()

                node = AstAssignment(operator=op.value, target=node, value=expression)
                node = set_location(node, node.target, node.value)

            elif isinstance(node, AstAttribute):
                with stream.syntax(assignment=pattern):
                    op = stream.get("assignment")

                if op:
                    expression = delegate("bolt:expression", stream)
                    target = AstTargetAttribute(
                        name=node.name,
                        value=node.value,
                    )
                    node = AstAssignment(
                        operator=op.value,
                        target=set_location(target, node),
                        value=expression,
                    )
                    node = set_location(node, node.target, node.value)

            elif isinstance(node, AstLookup):
                with stream.syntax(assignment=pattern):
                    op = stream.get("assignment")

                if op:
                    expression = delegate("bolt:expression", stream)
                    target = AstTargetItem(
                        value=node.value,
                        arguments=node.arguments,
                    )
                    node = AstAssignment(
                        operator=op.value,
                        target=set_location(target, node),
                        value=expression,
                    )
                    node = set_location(node, node.target, node.value)

            return node


@dataclass
class AssignmentTargetParser:
    """Parser for assignment targets."""

    allow_undefined_identifiers: bool = False
    allow_multiple: bool = False

    def __call__(self, stream: TokenStream) -> AstTarget:
        identifiers = get_stream_identifiers(stream)
        pending_identifiers = get_stream_pending_identifiers(stream)

        nodes: List[AstTarget] = []

        with stream.syntax(identifier=IDENTIFIER_PATTERN, comma=r","):
            while True:
                token = stream.expect("identifier")

                if self.allow_undefined_identifiers:
                    pending_identifiers.add(token.value)
                elif token.value not in identifiers:
                    exc = UndefinedIdentifier(token, identifiers)
                    raise set_location(exc, token)

                nodes.append(
                    set_location(AstTargetIdentifier(value=token.value), token)
                )

                if not self.allow_multiple or not stream.get("comma"):
                    break

        if len(nodes) == 1:
            return nodes[0]

        node = AstTargetUnpack(targets=AstChildren(nodes))
        return set_location(node, nodes[0], nodes[-1])


@dataclass
class IfElseLoweringParser:
    """Parser that turns elif statements into if statements in an else clause."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> AstRoot:
        node: AstRoot = self.parser(stream)

        changed = False
        result: List[AstCommand] = []

        commands = iter(node.commands)
        previous = ""

        for command in commands:
            if command.identifier in ["elif:condition:body", "else:body"]:
                if previous not in ["if:condition:body", "elif:condition:body"]:
                    exc = InvalidSyntax(
                        "Conditional branch must be part of an if statement."
                    )
                    raise set_location(exc, command)

            if command.identifier == "elif:condition:body":
                changed = True
                elif_chain = [command]

                for command in commands:
                    if command.identifier not in ["elif:condition:body", "else:body"]:
                        break
                    elif_chain.append(command)
                else:
                    command = None

                if elif_chain[-1].identifier == "else:body":
                    last = [elif_chain.pop()]
                else:
                    last = []

                for stmt in reversed(elif_chain):
                    stmt = replace(stmt, identifier="if:condition:body")
                    stmt = AstRoot(commands=AstChildren([stmt, *last]))
                    stmt = set_location(stmt, stmt.commands[0], stmt.commands[-1])
                    stmt = AstCommand(
                        identifier="else:body",
                        arguments=AstChildren([stmt]),
                    )
                    last = [set_location(stmt, stmt.arguments[0])]

                result.append(last[0])

            if not command:
                break

            previous = command.identifier
            result.append(command)

        if changed:
            node = replace(node, commands=AstChildren(result))

        return node


@dataclass
class BreakContinueConstraint:
    """Constraint that makes sure that break and continue statements only occur in loops."""

    parser: Parser
    allowed_scopes: Set[Tuple[str, ...]]

    def __call__(self, stream: TokenStream) -> AstRoot:
        scope = get_stream_scope(stream)
        loop = stream.data.get("loop") or scope in self.allowed_scopes

        with stream.provide(loop=loop):
            node: AstRoot = self.parser(stream)

        if not loop:
            for command in node.commands:
                if command.identifier in ["break", "continue"]:
                    exc = InvalidSyntax(
                        f"Can only use {command.identifier!r} in loops."
                    )
                    raise set_location(exc, command)

        return node


@dataclass
class FlushPendingIdentifiersParser:
    """Parser that flushes pending identifiers."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        identifiers = get_stream_identifiers(stream)
        pending_identifiers = get_stream_pending_identifiers(stream)

        identifiers |= pending_identifiers
        pending_identifiers.clear()

        return self.parser(stream)


def parse_function_signature(stream: TokenStream) -> AstFunctionSignature:
    """Parse function signature."""
    identifiers = get_stream_identifiers(stream)
    pending_identifiers = get_stream_pending_identifiers(stream)
    scoped_identifiers = set(identifiers)

    arguments: List[AstFunctionSignatureArgument] = []

    with stream.syntax(
        comma=r",",
        equal=r"=(?!=)",
        brace=r"\(|\)",
        identifier=IDENTIFIER_PATTERN,
    ):
        identifier = stream.expect("identifier")
        stream.expect(("brace", "("))

        scoped_identifiers.add(identifier.value)

        with stream.ignore("newline"):
            for _ in stream.peek_until(("brace", ")")):
                name = stream.expect("identifier")

                default = None
                if stream.get("equal"):
                    with stream.provide(
                        identifiers=scoped_identifiers | {arg.name for arg in arguments}
                    ):
                        default = delegate("bolt:expression", stream)

                argument = AstFunctionSignatureArgument(
                    name=name.value,
                    default=default,
                )
                arguments.append(set_location(argument, name, stream.current))

                if not stream.get("comma"):
                    stream.expect(("brace", ")"))
                    break

    identifiers.add(identifier.value)
    pending_identifiers |= {arg.name for arg in arguments}

    node = AstFunctionSignature(name=identifier.value, arguments=AstChildren(arguments))
    return set_location(node, identifier, stream.current)


def parse_function_root(stream: TokenStream) -> AstFunctionRoot:
    """Parse function root."""
    identifiers = get_stream_identifiers(stream)
    pending_identifiers = get_stream_pending_identifiers(stream)

    stream_copy = stream.copy()

    with stream.syntax(statement=r"[^\s#].*"):
        token = stream.expect("statement")
        while consume_line_continuation(stream):
            stream.expect("statement")

    stream_copy.data["identifiers"] = identifiers | pending_identifiers
    stream_copy.data["pending_identifiers"] = set()

    pending_identifiers.clear()

    node = AstFunctionRoot(stream=stream_copy)
    return set_location(node, token, stream.current)


def parse_del_target(stream: TokenStream) -> AstTarget:
    node = delegate("bolt:expression", stream)

    if isinstance(node, AstIdentifier):
        return set_location(AstTargetIdentifier(value=node.value), node)
    elif isinstance(node, AstAttribute):
        return set_location(AstTargetAttribute(name=node.name, value=node.value), node)
    elif isinstance(node, AstLookup):
        return set_location(
            AstTargetItem(value=node.value, arguments=node.arguments), node
        )

    exc = InvalidSyntax("Can only delete variables, attributes, or subscripted items.")
    raise set_location(exc, node)


def parse_identifier(stream: TokenStream) -> AstIdentifier:
    """Parse identifier."""
    identifiers = get_stream_identifiers(stream)

    with stream.syntax(
        true=TRUE_PATTERN,
        false=FALSE_PATTERN,
        null=NULL_PATTERN,
        identifier=IDENTIFIER_PATTERN,
    ):
        token = stream.expect("identifier")

    if token.value not in identifiers:
        exc = UndefinedIdentifier(token, identifiers)
        raise set_location(exc, token)

    return set_location(AstIdentifier(value=token.value), token)


@dataclass
class ImportLocationConstraint:
    """Constraint for import location."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        node: AstResourceLocation = self.parser(stream)

        if node.is_tag or node.namespace is None and not IMPORT_REGEX.match(node.path):
            exc = InvalidSyntax(f"Invalid module location {node.get_value()!r}.")
            raise set_location(exc, node)

        return node


@dataclass
class ImportStatementHandler:
    """Handle import statements."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        identifiers = get_stream_identifiers(stream)

        if isinstance(node := self.parser(stream), AstCommand):
            if node.identifier == "import:module":
                if isinstance(module := node.arguments[0], AstResourceLocation):
                    if module.namespace:
                        exc = InvalidSyntax(
                            f"Can't import {module.get_value()!r} without alias."
                        )
                        raise set_location(exc, module)
                    else:
                        identifiers.add(module.path.partition(".")[0])
            elif node.identifier == "import:module:as:alias":
                if isinstance(alias := node.arguments[1], AstImportedIdentifier):
                    identifiers.add(alias.value)
            elif node.identifier == "from:module:import:subcommand":
                subcommand = cast(AstCommand, node.arguments[1])
                while True:
                    if isinstance(
                        name := subcommand.arguments[0], AstImportedIdentifier
                    ):
                        identifiers.add(name.value)
                    if subcommand.identifier == "from:module:import:name:subcommand":
                        subcommand = cast(AstCommand, subcommand.arguments[1])
                    else:
                        break

        return node


def parse_import_name(stream: TokenStream) -> AstImportedIdentifier:
    """Parse import name."""
    with stream.syntax(name=IDENTIFIER_PATTERN, comma=r","):
        token = stream.expect("name")
        stream.get("comma")
        return set_location(AstImportedIdentifier(value=token.value), token)


@dataclass
class FunctionRootBacktracker:
    """Parser for backtracking over function root nodes."""

    parser: Parser = required_field()

    def __call__(self, stream: TokenStream) -> AstRoot:
        should_replace = False
        commands: List[AstCommand] = []

        node: AstRoot = self.parser(stream)

        identifiers = get_stream_identifiers(stream)

        for command in node.commands:
            if command.identifier == "def:function:body":
                if isinstance(function_root := command.arguments[-1], AstFunctionRoot):
                    should_replace = True

                    function_stream = function_root.stream
                    function_stream.data["identifiers"] |= identifiers
                    function_stream.data["function"] = True

                    command = replace(
                        command,
                        arguments=AstChildren(
                            [
                                *command.arguments[:-1],
                                delegate("nested_root", function_root.stream),
                            ]
                        ),
                    )

            commands.append(command)

        if should_replace:
            return replace(node, commands=AstChildren(commands))

        return node


@dataclass
class ReturnConstraint:
    """Constraint that makes sure that return statements only occur in functions."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> AstRoot:
        node: AstRoot = self.parser(stream)

        if stream.data.get("function"):
            return node

        for command in node.commands:
            if command.identifier in ["return", "return:value"]:
                exc = InvalidSyntax("Can only use 'return' in functions.")
                raise set_location(exc, command)

        return node


@dataclass
class YieldConstraint:
    """Constraint that makes sure that yield statements only occur in functions."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> AstRoot:
        node: AstRoot = self.parser(stream)

        if stream.data.get("function"):
            return node
        for command in node.commands:
            if command.identifier in ["yield", "yield:value", "yield:from:value"]:
                exc = InvalidSyntax("Can only use 'yield' in functions.")
                raise set_location(exc, command)

        return node


@dataclass
class BinaryParser:
    """Parser for binary expressions."""

    operators: List[str]
    parser: Parser
    right_associative: bool = False

    def __call__(self, stream: TokenStream) -> Any:
        with stream.syntax(operator="|".join(self.operators)):
            nodes = [self.parser(stream)]
            operations: List[str] = []

            for op in stream.collect("operator"):
                nodes.append(self.parser(stream))
                operations.append(normalize_whitespace(op.value))

        if self.right_associative:
            result = nodes[-1]
            nodes = nodes[-2::-1]
            operations = operations[::-1]
        else:
            result = nodes[0]
            nodes = nodes[1:]

        for op, node in zip(operations, nodes):
            if self.right_associative:
                result, node = node, result
            result = AstExpressionBinary(operator=op, left=result, right=node)
            result = set_location(result, result.left, result.right)

        return result


@dataclass
class UnaryParser:
    """Parser for unary expressions."""

    operators: List[str]
    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        with stream.syntax(operator="|".join(self.operators)):
            if op := stream.get("operator"):
                operator = normalize_whitespace(op.value)
                node = AstExpressionUnary(operator=operator, value=self(stream))
                return set_location(node, op, node.value)
            return self.parser(stream)


@dataclass
class UnpackParser:
    """Parser for unpacking."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        with stream.syntax(prefix=r"\*\*|\*"):
            prefix = stream.expect("prefix")

        node = self.parser(stream)

        node = AstUnpack(type="dict" if prefix.value == "**" else "list", value=node)
        return set_location(node, prefix, node.value)


@dataclass
class UnpackConstraint:
    """Constraint for unpacking."""

    type: str
    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        if isinstance(node := self.parser(stream), AstUnpack):
            if node.type != self.type:
                exc = InvalidSyntax(f"{node.type.capitalize()} unpacking not allowed.")
                raise node.emit_error(exc)
        return node


@dataclass
class KeywordParser:
    """Parser for keywords."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        with stream.syntax(name=IDENTIFIER_PATTERN, equal=r"=(?!=)"):
            name = stream.expect("name")
            stream.expect("equal")

        node = self.parser(stream)

        node = AstKeyword(name=name.value, value=node)
        return set_location(node, name, node.value)


@dataclass
class LookupParser:
    """Parser for lookups."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> Any:
        start = None
        stop = None
        step = None

        with stream.provide(bolt_lookup=True), stream.syntax(
            colon=r":",
            comma=r",",
            bracket=r"\]",
        ):
            colon1 = stream.get("colon")

            if not colon1:
                start = self.parser(stream)
                location = start.location
                colon1 = stream.get("colon")
            else:
                location = colon1.location

            if not colon1:
                return start

            colon2 = stream.get("colon")

            if not colon2:
                with stream.checkpoint():
                    sep = stream.get("comma", "bracket")
                if not sep:
                    stop = self.parser(stream)
                    colon2 = stream.get("colon")

            if colon2:
                with stream.checkpoint():
                    sep = stream.get("comma", "bracket")
                if not sep:
                    step = self.parser(stream)

        node = AstSlice(start=start, stop=stop, step=step)
        return set_location(node, location, stream.location)


@dataclass
class PrimaryParser:
    """Parser for primary expressions."""

    parser: Parser
    quote_helper: QuoteHelper = field(default_factory=JsonQuoteHelper)

    def __call__(self, stream: TokenStream) -> Any:
        with stream.syntax(brace=r"\(|\)", comma=r",", format_string=r"f['\"]"):
            token = stream.get(("brace", "("), "format_string")

            if token and token.match("brace"):
                with stream.ignore("newline"):
                    comma = None
                    items: List[AstExpression] = []

                    for _ in stream.peek_until(("brace", ")")):
                        items.append(delegate("bolt:expression", stream))

                        if not (comma := stream.get("comma")):
                            stream.expect(("brace", ")"))
                            break

                    if len(items) == 1 and not comma:
                        node = items[0]
                    else:
                        node = AstTuple(items=AstChildren(items))
                        node = set_location(node, token, stream.current)

            elif token and token.match("format_string"):
                quote = token.value[-1]

                with stream.provide(bolt_format_string=True), stream.syntax(
                    escape=rf"\\.",
                    double_brace=r"\{\{|\}\}",
                    brace=r"\{|\}",
                    quote=quote,
                    text=r"[^\\]+?",
                ):
                    fmt = quote
                    values: List[AstExpression] = []

                    for escape, double_brace, brace, text in stream.collect(
                        "escape",
                        "double_brace",
                        ("brace", "{"),
                        "text",
                    ):
                        if escape:
                            fmt += escape.value
                        elif double_brace:
                            fmt += double_brace.value
                        elif brace:
                            fmt += "{"
                            with stream.syntax(text=None):
                                values.append(delegate("bolt:expression", stream))
                            with stream.syntax(spec=r"[:!][^\}]+", double_brace=None):
                                if spec := stream.get("spec"):
                                    fmt += spec.value
                                stream.expect(("brace", "}"))
                            fmt += "}"
                        elif text:
                            fmt += text.value

                    end_quote = stream.expect("quote")
                    fmt += end_quote.value

                    fmt = self.quote_helper.unquote_string(
                        Token(
                            "format_string",
                            fmt,
                            token.location.with_horizontal_offset(1),
                            end_quote.end_location,
                        )
                    )

                    node = AstFormatString(fmt=fmt, values=AstChildren(values))
                    node = set_location(node, token, end_quote)

            else:
                node = self.parser(stream)

        with stream.syntax(
            dot=r"\.",
            comma=r",",
            brace=r"\(|\)",
            bracket=r"\[|\]",
            identifier=IDENTIFIER_PATTERN,
            string=STRING_PATTERN,
            number=r"(?:0|[1-9][0-9]*)",
        ):
            while token := stream.get("dot", ("brace", "("), ("bracket", "[")):
                arguments: List[Any] = []

                if token.match("dot"):
                    identifier, string, number = stream.expect(
                        "identifier",
                        "string",
                        "number",
                    )

                    if identifier:
                        node = AstAttribute(value=node, name=identifier.value)
                        node = set_location(node, node.value, identifier)
                        continue

                    if string:
                        value = self.quote_helper.unquote_string(string)
                    elif number:
                        value = int(number.value)

                    arguments.append(set_location(AstValue(value=value), stream.current))  # type: ignore

                else:
                    if token.match("brace"):
                        close = ("brace", ")")
                        argument_parser = delegate("bolt:call_argument")
                    else:
                        close = ("bracket", "]")
                        argument_parser = delegate("bolt:lookup_argument")

                    allow_positional = True

                    with stream.ignore("newline"):
                        for _ in stream.peek_until(close):
                            argument = argument_parser(stream)

                            if isinstance(argument, AstKeyword):
                                allow_positional = False
                            elif isinstance(argument, AstUnpack):
                                if argument.type == "dict":
                                    allow_positional = False
                                elif not allow_positional:
                                    exc = InvalidSyntax(
                                        "List unpacking not allowed after keyword arguments."
                                    )
                                    raise argument.emit_error(exc)
                            elif not allow_positional:
                                exc = InvalidSyntax(
                                    "Positional argument not allowed after keyword arguments."
                                )
                                raise argument.emit_error(exc)

                            arguments.append(argument)

                            if not stream.get("comma"):
                                stream.expect(close)
                                break

                if token.match("brace"):
                    node = AstCall(value=node, arguments=AstChildren(arguments))
                elif not arguments:
                    exc = InvalidSyntax("Empty lookup not allowed.")
                    raise set_location(exc, node, stream.current)
                else:
                    node = AstLookup(value=node, arguments=AstChildren(arguments))

                node = set_location(node, node.value, stream.current)

        return node


def parse_dict_item(stream: TokenStream) -> Any:
    """Parse dict item node."""
    identifiers = get_stream_identifiers(stream)

    with stream.syntax(colon=r":", identifier=IDENTIFIER_PATTERN):
        with stream.checkpoint() as commit:
            identifier = stream.expect("identifier")
            stream.expect("colon")
            commit()

            if identifier.value in identifiers:
                key = AstIdentifier(value=identifier.value)
            else:
                key = AstValue(value=identifier.value)

            key = set_location(key, identifier)

        if commit.rollback:
            key = delegate("bolt:expression", stream)
            stream.expect("colon")

        value = delegate("bolt:expression", stream)

    item = AstDictItem(key=key, value=value)
    return set_location(item, key, value)


@dataclass
class LiteralParser:
    """Parser for literals."""

    database: CompilationDatabase
    quote_helper: QuoteHelper = field(default_factory=JsonQuoteHelper)

    def __call__(self, stream: TokenStream) -> Any:
        with stream.syntax(
            curly=r"\{|\}",
            bracket=r"\[|\]",
            comma=r",",
            true=TRUE_PATTERN,
            false=FALSE_PATTERN,
            null=NULL_PATTERN,
            string=STRING_PATTERN,
            resource=(
                None
                if stream.data.get("bolt_lookup")
                or stream.data.get("bolt_format_string")
                else RESOURCE_LOCATION_PATTERN
            ),
            number=NUMBER_PATTERN,
        ):
            curly, bracket, true, false, null, string, resource, number = stream.expect(
                ("curly", "{"),
                ("bracket", "["),
                "true",
                "false",
                "null",
                "string",
                "resource",
                "number",
            )

            if curly:
                items: List[Any] = []

                with stream.ignore("newline"):
                    for _ in stream.peek_until(("curly", "}")):
                        items.append(delegate("bolt:dict_item", stream))

                        if not stream.get("comma"):
                            stream.expect(("curly", "}"))
                            break

                node = AstDict(items=AstChildren(items))
                return set_location(node, curly, stream.current)

            if bracket:
                elements: List[Any] = []

                with stream.ignore("newline"):
                    for _ in stream.peek_until(("bracket", "]")):
                        elements.append(delegate("bolt:list_item", stream))

                        if not stream.get("comma"):
                            stream.expect(("bracket", "]"))
                            break

                node = AstList(items=AstChildren(elements))
                return set_location(node, bracket, stream.current)

            if true:
                value = True
            elif false:
                value = False
            elif null:
                value = None
            elif string:
                value = self.quote_helper.unquote_string(string)
            elif resource:
                if resource.value.startswith(("./", "../")):
                    value = ":".join(
                        resolve_using_database(
                            relative_path=resource.value,
                            database=self.database,
                            location=resource.location,
                            end_location=resource.end_location,
                        )
                    )
                else:
                    value = resource.value
            elif number:
                value = string_to_number(number.value)

            node = AstValue(value=value)  # type: ignore
            return set_location(node, stream.current)
