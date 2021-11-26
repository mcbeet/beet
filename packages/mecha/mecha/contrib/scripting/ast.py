__all__ = [
    "AstExpression",
    "AstExpressionBinary",
    "AstExpressionUnary",
    "AstValue",
    "AstIdentifier",
    "AstAssignment",
]


from dataclasses import dataclass
from typing import Any

from beet.core.utils import required_field

from mecha import AstNode


@dataclass(frozen=True)
class AstExpression(AstNode):
    """Base ast node for expressions."""


@dataclass(frozen=True)
class AstExpressionBinary(AstExpression):
    """Ast expression binary node."""

    operator: str = required_field()
    left: AstExpression = required_field()
    right: AstExpression = required_field()


@dataclass(frozen=True)
class AstExpressionUnary(AstExpression):
    """Ast expression unary node."""

    operator: str = required_field()
    value: AstExpression = required_field()


@dataclass(frozen=True)
class AstValue(AstExpression):
    """Ast value node."""

    value: Any = required_field()


@dataclass(frozen=True)
class AstIdentifier(AstExpression):
    """Ast identifier node."""

    value: str = required_field()


@dataclass(frozen=True)
class AstAssignment(AstNode):
    """Ast assignment node."""

    left: AstIdentifier = required_field()
    right: AstExpression = required_field()
