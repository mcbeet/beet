__all__ = [
    "get_scripting_parsers",
    "get_stream_identifiers",
    "get_stream_pending_identifiers",
    "UndefinedIdentifier",
    "parse_statement",
    "AssignmentTargetParser",
    "IfElseConstraint",
    "BreakContinueConstraint",
    "FlushPendingIdentifiersParser",
    "BinaryParser",
    "UnaryParser",
    "AtomParser",
]


from dataclasses import dataclass, field
from difflib import get_close_matches
from typing import Any, Dict, Iterable, List, Set, Tuple

from tokenstream import InvalidSyntax, Token, TokenStream, UnexpectedToken, set_location

from mecha import AstRoot, Parser, ResetSyntaxParser, delegate, get_stream_scope
from mecha.utils import (
    QuoteHelper,
    QuoteHelperWithUnicode,
    normalize_whitespace,
    string_to_number,
)

from .ast import (
    AstAssignment,
    AstAssignmentTarget,
    AstAssignmentTargetIdentifier,
    AstExpressionBinary,
    AstExpressionUnary,
    AstIdentifier,
    AstValue,
)

IDENTIFIER_PATTERN: str = r"[a-zA-Z_][a-zA-Z0-9_]*"


def get_scripting_parsers(parsers: Dict[str, Parser]) -> Dict[str, Parser]:
    """Return the scripting parsers."""
    return {
        ################################################################################
        # Command
        ################################################################################
        "root": FlushPendingIdentifiersParser(
            BreakContinueConstraint(
                parser=IfElseConstraint(parsers["root"]),
                allowed_scopes={
                    ("while", "condition", "body"),
                    ("for", "target", "in", "iterable", "body"),
                },
            )
        ),
        "nested_root": FlushPendingIdentifiersParser(
            BreakContinueConstraint(
                parser=IfElseConstraint(parsers["nested_root"]),
                allowed_scopes={
                    ("while", "condition", "body"),
                    ("for", "target", "in", "iterable", "body"),
                },
            )
        ),
        "command:argument:mecha:scripting:statement": ResetSyntaxParser(
            delegate("scripting:statement")
        ),
        "command:argument:mecha:scripting:assignment_target": ResetSyntaxParser(
            delegate("scripting:assignment_target")
        ),
        "command:argument:mecha:scripting:expression": ResetSyntaxParser(
            delegate("scripting:expression")
        ),
        ################################################################################
        # Scripting
        ################################################################################
        "scripting:statement": parse_statement,
        "scripting:assignment_target": AssignmentTargetParser(
            allow_undefined_identifiers=True
        ),
        "scripting:augmented_assignment_target": AssignmentTargetParser(),
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
        "scripting:primary": delegate("scripting:atom"),
        "scripting:atom": AtomParser(),
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
class AtomParser:
    """Parser for atoms."""

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

    def __call__(self, stream: TokenStream) -> Any:
        identifiers = get_stream_identifiers(stream)

        with stream.syntax(
            brace=r"\(|\)",
            true=r"\b[tT]rue\b",
            false=r"\b[fF]alse\b",
            null=r"\b(?:null|None)\b",
            identifier=IDENTIFIER_PATTERN,
            string=r'"(?:\\.|[^\\\n])*?"' "|" r"'(?:\\.|[^\\\n])*?'",
            number=r"(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?\b",
        ):
            brace, true, false, null, identifier, string, number = stream.expect(
                ("brace", "("),
                "true",
                "false",
                "null",
                "identifier",
                "string",
                "number",
            )

            if brace:
                with stream.ignore("newline"):
                    inner = delegate("scripting:expression", stream)
                    stream.expect(("brace", ")"))
                return inner

            if identifier:
                if identifier.value not in identifiers:
                    exc = UndefinedIdentifier(identifier, identifiers)
                    raise set_location(exc, identifier)
                return set_location(AstIdentifier(value=identifier.value), identifier)

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
