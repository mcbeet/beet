__all__ = [
    "AstExpression",
    "AstExpressionBinary",
    "AstExpressionUnary",
    "AstValue",
    "AstIdentifier",
    "AstFormatString",
    "AstTuple",
    "AstList",
    "AstDictItem",
    "AstDict",
    "AstUnpack",
    "AstKeyword",
    "AstAttribute",
    "AstLookup",
    "AstCall",
    "AstAssignmentTarget",
    "AstAssignmentTargetIdentifier",
    "AstAssignmentTargetAttribute",
    "AstAssignmentTargetItem",
    "AstAssignment",
    "AstFunctionSignature",
    "AstFunctionSignatureArgument",
    "AstFunctionRoot",
    "AstInterpolation",
    "AstImportedIdentifier",
]


from dataclasses import dataclass
from typing import Any, ClassVar, Optional, Union

from beet.core.utils import required_field
from tokenstream import TokenStream

from mecha import AstChildren, AstNode


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
class AstFormatString(AstExpression):
    """Ast format string node."""

    fmt: str = required_field()
    values: AstChildren[AstExpression] = required_field()


@dataclass(frozen=True)
class AstTuple(AstExpression):
    """Ast tuple node."""

    items: AstChildren[AstExpression] = required_field()


@dataclass(frozen=True)
class AstList(AstExpression):
    """Ast list node."""

    items: AstChildren[AstExpression] = required_field()


@dataclass(frozen=True)
class AstDictItem(AstNode):
    """Ast dict item node."""

    key: AstExpression = required_field()
    value: AstExpression = required_field()


@dataclass(frozen=True)
class AstDict(AstExpression):
    """Ast dict node."""

    items: AstChildren[AstDictItem] = required_field()


@dataclass(frozen=True)
class AstUnpack(AstNode):
    """Ast unpack node."""

    type: str = required_field()
    value: AstExpression = required_field()


@dataclass(frozen=True)
class AstKeyword(AstNode):
    """Ast keyword node."""

    name: str = required_field()
    value: AstExpression = required_field()


@dataclass(frozen=True)
class AstAttribute(AstExpression):
    """Ast attribute node."""

    name: str = required_field()
    value: AstExpression = required_field()


@dataclass(frozen=True)
class AstLookup(AstExpression):
    """Ast lookup node."""

    value: AstExpression = required_field()
    arguments: AstChildren[AstExpression] = required_field()


@dataclass(frozen=True)
class AstCall(AstExpression):
    """Ast call node."""

    value: AstExpression = required_field()
    arguments: AstChildren[
        Union[AstExpression, AstUnpack, AstKeyword]
    ] = required_field()


@dataclass(frozen=True)
class AstAssignmentTarget(AstNode):
    """Base node for assignment targets."""

    multiple: ClassVar[bool] = False


@dataclass(frozen=True)
class AstAssignmentTargetIdentifier(AstAssignmentTarget):
    """Ast assignment target identifier node."""

    value: str = required_field()


@dataclass(frozen=True)
class AstAssignmentTargetAttribute(AstAssignmentTarget):
    """Ast assignment target attribute node."""

    name: str = required_field()
    value: AstExpression = required_field()


@dataclass(frozen=True)
class AstAssignmentTargetItem(AstAssignmentTarget):
    """Ast assignment target item node."""

    value: AstExpression = required_field()
    arguments: AstChildren[AstExpression] = required_field()


@dataclass(frozen=True)
class AstAssignment(AstNode):
    """Ast assignment node."""

    operator: str = required_field()
    target: AstAssignmentTarget = required_field()
    value: AstExpression = required_field()


@dataclass(frozen=True)
class AstFunctionSignatureArgument(AstNode):
    """Ast function signature argument node."""

    name: str = required_field()
    default: Optional[AstExpression] = None


@dataclass(frozen=True)
class AstFunctionSignature(AstNode):
    """Ast function signature node."""

    name: str = required_field()
    arguments: AstChildren[AstFunctionSignatureArgument] = required_field()


@dataclass(frozen=True)
class AstFunctionRoot(AstNode):
    """Ast function root node."""

    stream: TokenStream = required_field()


@dataclass(frozen=True)
class AstInterpolation(AstNode):
    """Ast interpolation node."""

    converter: str = required_field()
    value: AstExpression = required_field()


@dataclass(frozen=True)
class AstImportedIdentifier(AstNode):
    """Ast imported identifier node."""

    value: str = required_field()
