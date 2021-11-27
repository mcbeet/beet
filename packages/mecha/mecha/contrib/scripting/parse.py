__all__ = [
    "get_scripting_parsers",
    "get_stream_identifiers",
    "UndefinedIdentifier",
    "parse_statement",
    "IfElseConstraint",
    "BinaryParser",
    "UnaryParser",
    "AtomParser",
]


from dataclasses import dataclass, field
from difflib import get_close_matches
from typing import Any, Dict, List, Set

from tokenstream import InvalidSyntax, Token, TokenStream, UnexpectedToken, set_location

from mecha import AstRoot, Parser, ResetSyntaxParser, delegate
from mecha.utils import (
    QuoteHelper,
    QuoteHelperWithUnicode,
    normalize_whitespace,
    string_to_number,
)

from .ast import (
    AstAssignment,
    AstExpressionBinary,
    AstExpressionUnary,
    AstIdentifier,
    AstValue,
)

IDENTIFIER_PATTERN: str = r"[a-zA-Z_][a-zA-Z0-9_]*"


def get_scripting_parsers(parsers: Dict[str, Parser]) -> Dict[str, Parser]:
    """Return the scripting parsers."""
    parsers = {
        "root": IfElseConstraint(parsers["root"]),
        "nested_root": IfElseConstraint(parsers["nested_root"]),
        "scripting:statement": parse_statement,
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

    for arg in ["scripting:statement", "scripting:expression"]:
        parsers[f"command:argument:mecha:{arg}"] = ResetSyntaxParser(delegate(arg))

    return parsers


def get_stream_identifiers(stream: TokenStream) -> Set[str]:
    """Return the set of accessible identifiers currently associated with the token stream."""
    return stream.data.setdefault("identifiers", set())


class UndefinedIdentifier(UnexpectedToken):
    """Raised when an identifier is not defined."""

    identifiers: Set[str]

    def __init__(self, token: Token, identifiers: Set[str]):
        super().__init__(token)
        self.identifiers = identifiers

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

    with stream.syntax(
        equal=r"=",
        identifier=IDENTIFIER_PATTERN,
    ):
        with stream.checkpoint() as commit:
            token = stream.expect("identifier")
            stream.expect("equal")
            commit()

            identifier = set_location(AstIdentifier(value=token.value), token)
            expression = delegate("scripting:expression", stream)

            identifiers.add(identifier.value)

            node = AstAssignment(left=identifier, right=expression)
            node = set_location(node, identifier, expression)

    if commit.rollback:
        node = delegate("scripting:expression", stream)

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
                if (
                    stream.data.get("check_identifiers", True)
                    and identifier.value not in identifiers
                ):
                    stream.index -= 1
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
