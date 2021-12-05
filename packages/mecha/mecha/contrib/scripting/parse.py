__all__ = [
    "get_scripting_parsers",
    "get_stream_identifiers",
    "get_stream_pending_identifiers",
    "UndefinedIdentifier",
    "create_scripting_root_parser",
    "ExecuteIfConditionConstraint",
    "InterpolationParser",
    "parse_statement",
    "AssignmentTargetParser",
    "IfElseConstraint",
    "BreakContinueConstraint",
    "FlushPendingIdentifiersParser",
    "parse_function_signature",
    "parse_function_root",
    "parse_identifier",
    "ImportLocationConstraint",
    "ImportStatementHandler",
    "FunctionRootBacktracker",
    "ReturnConstraint",
    "YieldConstraint",
    "BinaryParser",
    "UnaryParser",
    "PrimaryParser",
    "LiteralParser",
]


import re
from dataclasses import dataclass, field, replace
from difflib import get_close_matches
from typing import Any, Dict, Iterable, List, Set, Tuple, cast

from beet.core.utils import required_field
from tokenstream import InvalidSyntax, Token, TokenStream, UnexpectedToken, set_location

from mecha import (
    AlternativeParser,
    AstChildren,
    AstCommand,
    AstLiteral,
    AstResourceLocation,
    AstRoot,
)
from mecha import LiteralParser as BasicLiteralParser
from mecha import Parser, consume_line_continuation, delegate, get_stream_scope
from mecha.utils import QuoteHelper, normalize_whitespace, string_to_number

from .ast import (
    AstAssignment,
    AstAssignmentTarget,
    AstAssignmentTargetIdentifier,
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
    AstInterpolation,
    AstList,
    AstLookup,
    AstTuple,
    AstValue,
)
from .utils import ScriptingQuoteHelper

TRUE_PATTERN: str = r"\b[tT]rue\b"
FALSE_PATTERN: str = r"\b[fF]alse\b"
NULL_PATTERN: str = r"\b(?:null|None)\b"
IDENTIFIER_PATTERN: str = r"(?!_mecha_)[a-zA-Z_][a-zA-Z0-9_]*"
STRING_PATTERN: str = r'"(?:\\.|[^\\\n])*?"' "|" r"'(?:\\.|[^\\\n])*?'"
NUMBER_PATTERN: str = r"(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?\b"

IMPORT_REGEX = re.compile(fr"^{IDENTIFIER_PATTERN}(?:\.{IDENTIFIER_PATTERN})*$")


def get_scripting_parsers(parsers: Dict[str, Parser]) -> Dict[str, Parser]:
    """Return the scripting parsers."""
    return {
        ################################################################################
        # Command
        ################################################################################
        "root": create_scripting_root_parser(parsers["root"]),
        "nested_root": create_scripting_root_parser(parsers["nested_root"]),
        "command": ImportStatementHandler(
            ExecuteIfConditionConstraint(parsers["command"])
        ),
        "command:argument:mecha:scripting:statement": delegate("scripting:statement"),
        "command:argument:mecha:scripting:assignment_target": delegate(
            "scripting:assignment_target"
        ),
        "command:argument:mecha:scripting:import": delegate("scripting:import"),
        "command:argument:mecha:scripting:import_name": delegate(
            "scripting:import_name"
        ),
        "command:argument:mecha:scripting:expression": delegate("scripting:expression"),
        "command:argument:mecha:scripting:function_signature": delegate(
            "scripting:function_signature"
        ),
        "command:argument:mecha:scripting:function_root": delegate(
            "scripting:function_root"
        ),
        ################################################################################
        # Scripting
        ################################################################################
        "scripting:statement": parse_statement,
        "scripting:assignment_target": AssignmentTargetParser(
            allow_undefined_identifiers=True
        ),
        "scripting:augmented_assignment_target": AssignmentTargetParser(),
        "scripting:function_signature": parse_function_signature,
        "scripting:function_root": parse_function_root,
        "scripting:interpolation": PrimaryParser(delegate("scripting:identifier")),
        "scripting:identifier": parse_identifier,
        "scripting:import": ImportLocationConstraint(
            parsers["resource_location_or_tag"]
        ),
        "scripting:import_name": BasicLiteralParser("name", IDENTIFIER_PATTERN),
        "scripting:expression": delegate("scripting:disjunction"),
        "scripting:disjunction": BinaryParser(
            operators=[r"\bor\b"],
            parser=delegate("scripting:conjunction"),
        ),
        "scripting:conjunction": BinaryParser(
            operators=[r"\band\b"],
            parser=delegate("scripting:inversion"),
        ),
        "scripting:inversion": UnaryParser(
            operators=[r"\bnot\b"],
            parser=delegate("scripting:comparison"),
        ),
        "scripting:comparison": BinaryParser(
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
            parser=delegate("scripting:bitwise_or"),
        ),
        "scripting:bitwise_or": BinaryParser(
            operators=[r"\|"],
            parser=delegate("scripting:bitwise_xor"),
        ),
        "scripting:bitwise_xor": BinaryParser(
            operators=[r"\^"],
            parser=delegate("scripting:bitwise_and"),
        ),
        "scripting:bitwise_and": BinaryParser(
            operators=["&"],
            parser=delegate("scripting:shift_expr"),
        ),
        "scripting:shift_expr": BinaryParser(
            operators=["<<", ">>"],
            parser=delegate("scripting:sum"),
        ),
        "scripting:sum": BinaryParser(
            operators=[r"\+", "-"],
            parser=delegate("scripting:term"),
        ),
        "scripting:term": BinaryParser(
            operators=[r"\*", "//", "/", "%"],
            parser=delegate("scripting:factor"),
        ),
        "scripting:factor": UnaryParser(
            operators=[r"\+", "-", "~"],
            parser=delegate("scripting:power"),
        ),
        "scripting:power": BinaryParser(
            operators=[r"\*\*"],
            parser=delegate("scripting:primary"),
            right_associative=True,
        ),
        "scripting:primary": PrimaryParser(delegate("scripting:atom")),
        "scripting:atom": AlternativeParser(
            [
                delegate("scripting:identifier"),
                delegate("scripting:literal"),
            ]
        ),
        "scripting:literal": LiteralParser(),
        ################################################################################
        # Interpolation
        ################################################################################
        "literal": InterpolationParser("literal", parsers["literal"]),
        "bool": InterpolationParser("bool", parsers["bool"]),
        "numeric": InterpolationParser("numeric", parsers["numeric"]),
        "time": InterpolationParser("time", parsers["time"]),
        "word": InterpolationParser("literal", parsers["word"]),
        "phrase": InterpolationParser("string", parsers["phrase"]),
        "greedy": InterpolationParser("literal", parsers["greedy"]),
        "json": InterpolationParser("json", parsers["json"]),
        "nbt": InterpolationParser("nbt", parsers["nbt"]),
        "range": InterpolationParser("range", parsers["range"]),
        "resource_location_or_tag": InterpolationParser(
            "resource_location", parsers["resource_location_or_tag"]
        ),
        "objective": InterpolationParser("literal", parsers["objective"]),
        "swizzle": InterpolationParser("literal", parsers["swizzle"]),
        "team": InterpolationParser("literal", parsers["team"]),
        "command:argument:minecraft:message": InterpolationParser(
            "message", parsers["command:argument:minecraft:message"]
        ),
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


def create_scripting_root_parser(parser: Parser):
    """Return parser for the root node when using scripting."""
    return FunctionRootBacktracker(
        FlushPendingIdentifiersParser(
            ReturnConstraint(
                YieldConstraint(
                    BreakContinueConstraint(
                        parser=IfElseConstraint(parser),
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

    def __call__(self, stream: TokenStream) -> Any:
        for parser, alternative in stream.choose("interpolation", "argument"):
            with alternative:
                if parser == "interpolation":
                    node = delegate("scripting:interpolation", stream)
                    node = AstInterpolation(converter=self.converter, value=node)
                    return set_location(node, node.value)
                elif parser == "argument":
                    return self.parser(stream)


def parse_statement(stream: TokenStream) -> Any:
    """Parse statement."""
    identifiers = get_stream_identifiers(stream)
    pending_identifiers = get_stream_pending_identifiers(stream)

    for parser, alternative in stream.choose(
        "scripting:augmented_assignment_target",
        "scripting:assignment_target",
        "scripting:expression",
    ):
        with alternative:
            pending_identifiers.clear()
            node = delegate(parser, stream)

            if isinstance(node, AstAssignmentTarget):
                pattern = r"=(?!=)"

                if (
                    parser == "scripting:augmented_assignment_target"
                    and not node.multiple
                ):
                    pattern += r"|\+=|-=|\*=|//=|/=|%=|&=|\|=|\^=|<<=|>>=|\*\*="

                with stream.syntax(assignment=pattern):
                    op = stream.expect("assignment")

                expression = delegate("scripting:expression", stream)

                identifiers |= pending_identifiers
                pending_identifiers.clear()

                node = AstAssignment(operator=op.value, target=node, value=expression)
                node = set_location(node, node.target, node.value)

            return node


@dataclass
class AssignmentTargetParser:
    """Parser for assignment targets."""

    allow_undefined_identifiers: bool = False

    def __call__(self, stream: TokenStream) -> AstAssignmentTarget:
        identifiers = get_stream_identifiers(stream)
        pending_identifiers = get_stream_pending_identifiers(stream)

        with stream.syntax(identifier=IDENTIFIER_PATTERN):
            token = stream.expect("identifier")

            if self.allow_undefined_identifiers:
                pending_identifiers.add(token.value)
            elif token.value not in identifiers:
                exc = UndefinedIdentifier(token, identifiers)
                raise set_location(exc, token)

            node = set_location(AstAssignmentTargetIdentifier(value=token.value), token)

        return node


@dataclass
class IfElseConstraint:
    """Constraint that makes sure that if statements are properly formed."""

    parser: Parser

    def __call__(self, stream: TokenStream) -> AstRoot:
        node: AstRoot = self.parser(stream)

        previous = ""

        for command in node.commands:
            if command.identifier in ["elif:condition:body", "else:body"]:
                if previous not in ["if:condition:body", "elif:condition:body"]:
                    exc = InvalidSyntax(
                        "Conditional branch must be part of an if statement."
                    )
                    raise set_location(exc, command)
            previous = command.identifier

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
                        default = delegate("scripting:expression", stream)

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
                if isinstance(alias := node.arguments[1], AstLiteral):
                    identifiers.add(alias.value)
            elif node.identifier == "from:module:import:subcommand":
                subcommand = cast(AstCommand, node.arguments[1])
                while True:
                    if isinstance(name := subcommand.arguments[0], AstLiteral):
                        identifiers.add(name.value)
                    if subcommand.identifier == "from:module:import:name:subcommand":
                        subcommand = cast(AstCommand, subcommand.arguments[1])
                    else:
                        break

        return node


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
                    function_stream.data.update(
                        properties={"check_nesting": False},
                        function=True,
                    )

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
class PrimaryParser:
    """Parser for primary expressions."""

    parser: Parser
    quote_helper: QuoteHelper = field(default_factory=ScriptingQuoteHelper)

    def __call__(self, stream: TokenStream) -> Any:
        with stream.syntax(brace=r"\(|\)", comma=r",", format_string=r"f['\"]"):
            token = stream.get(("brace", "("), "format_string")

            if token and token.match("brace"):
                with stream.ignore("newline"):
                    comma = None
                    items: List[AstExpression] = []

                    for _ in stream.peek_until(("brace", ")")):
                        items.append(delegate("scripting:expression", stream))

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

                with stream.syntax(
                    escape=fr"\\.",
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
                                values.append(delegate("scripting:expression", stream))
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
                arguments: List[AstExpression] = []

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

                    arguments.append(
                        set_location(AstValue(value=value), stream.current)
                    )

                else:
                    close = ("brace", ")") if token.match("brace") else ("bracket", "]")

                    with stream.ignore("newline"):
                        for _ in stream.peek_until(close):
                            arguments.append(delegate("scripting:expression", stream))

                            if not stream.get("comma"):
                                stream.expect(close)
                                break

                if token.match("brace"):
                    node = AstCall(value=node, arguments=AstChildren(arguments))
                else:
                    node = AstLookup(value=node, arguments=AstChildren(arguments))

                node = set_location(node, node.value, stream.current)

        return node


@dataclass
class LiteralParser:
    """Parser for literals."""

    quote_helper: QuoteHelper = field(default_factory=ScriptingQuoteHelper)

    def __call__(self, stream: TokenStream) -> Any:
        identifiers = get_stream_identifiers(stream)

        with stream.syntax(
            curly=r"\{|\}",
            bracket=r"\[|\]",
            colon=r":",
            comma=r",",
            true=TRUE_PATTERN,
            false=FALSE_PATTERN,
            null=NULL_PATTERN,
            identifier=IDENTIFIER_PATTERN,
            string=STRING_PATTERN,
            number=NUMBER_PATTERN,
        ):
            curly, bracket, true, false, null, string, number = stream.expect(
                ("curly", "{"),
                ("bracket", "["),
                "true",
                "false",
                "null",
                "string",
                "number",
            )

            if curly:
                items: List[AstDictItem] = []

                with stream.ignore("newline"):
                    for _ in stream.peek_until(("curly", "}")):
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
                            key = delegate("scripting:expression", stream)
                            stream.expect("colon")

                        value = delegate("scripting:expression", stream)

                        item = AstDictItem(key=key, value=value)
                        items.append(set_location(item, key, value))

                        if not stream.get("comma"):
                            stream.expect(("curly", "}"))
                            break

                node = AstDict(items=AstChildren(items))
                return set_location(node, curly, stream.current)

            if bracket:
                elements: List[AstExpression] = []

                with stream.ignore("newline"):
                    for _ in stream.peek_until(("bracket", "]")):
                        elements.append(delegate("scripting:expression", stream))

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
            elif number:
                value = string_to_number(number.value)

            node = AstValue(value=value)  # type: ignore
            return set_location(node, stream.current)
