__all__ = [
    "AstModuleRoot",
    "AstExpression",
    "AstExpressionBinary",
    "AstExpressionUnary",
    "AstValue",
    "AstIdentifier",
    "AstFormatString",
    "AstTuple",
    "AstList",
    "AstDict",
    "AstDictItem",
    "AstDictUnquotedKey",
    "AstSlice",
    "AstUnpack",
    "AstKeyword",
    "AstAttribute",
    "AstLookup",
    "AstCall",
    "AstTarget",
    "AstTargetIdentifier",
    "AstTargetUnpack",
    "AstTargetAttribute",
    "AstTargetItem",
    "AstAssignment",
    "AstDecorator",
    "AstFunctionSignature",
    "AstFunctionSignatureElement",
    "AstFunctionSignatureArgument",
    "AstFunctionSignaturePositionalMarker",
    "AstFunctionSignatureVariadicArgument",
    "AstFunctionSignatureVariadicMarker",
    "AstFunctionSignatureVariadicKeywordArgument",
    "AstDeferredRoot",
    "AstMacro",
    "AstMacroCall",
    "AstMacroLiteral",
    "AstMacroArgument",
    "AstMacroMatch",
    "AstMacroMatchLiteral",
    "AstMacroMatchArgument",
    "AstProcMacro",
    "AstProcMacroMarker",
    "AstProcMacroResult",
    "AstClassName",
    "AstClassBases",
    "AstClassRoot",
    "AstInterpolation",
    "AstFromImport",
    "AstImportedItem",
    "AstImportedMacro",
]


import re
from dataclasses import dataclass
from typing import Any, Optional, Union

from beet.core.utils import JsonDict, required_field
from mecha import (
    AstChildren,
    AstCommand,
    AstJson,
    AstLiteral,
    AstNode,
    AstResourceLocation,
    AstRoot,
)
from tokenstream import TokenStream

from .pattern import IDENTIFIER_PATTERN


@dataclass(frozen=True)
class AstModuleRoot(AstRoot):
    """Module root ast node."""


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
class AstDictUnquotedKey(AstValue):
    """Ast dict unquoted key node."""


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
class AstSlice(AstNode):
    """Ast slice node."""

    start: Optional[AstExpression] = None
    stop: Optional[AstExpression] = None
    step: Optional[AstExpression] = None


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
    arguments: AstChildren[Union[AstExpression, AstSlice]] = required_field()


@dataclass(frozen=True)
class AstCall(AstExpression):
    """Ast call node."""

    value: AstExpression = required_field()
    arguments: AstChildren[
        Union[AstExpression, AstUnpack, AstKeyword]
    ] = required_field()


@dataclass(frozen=True)
class AstTarget(AstNode):
    """Base node for targets."""


@dataclass(frozen=True)
class AstTargetIdentifier(AstTarget):
    """Ast target identifier node."""

    value: str = required_field()
    rebind: bool = False


@dataclass(frozen=True)
class AstTargetUnpack(AstTarget):
    """Ast target unpack node."""

    targets: AstChildren[AstTarget] = required_field()


@dataclass(frozen=True)
class AstTargetAttribute(AstTarget):
    """Ast target attribute node."""

    name: str = required_field()
    value: AstExpression = required_field()


@dataclass(frozen=True)
class AstTargetItem(AstTarget):
    """Ast target item node."""

    value: AstExpression = required_field()
    arguments: AstChildren[Union[AstExpression, AstSlice]] = required_field()


@dataclass(frozen=True)
class AstAssignment(AstNode):
    """Ast assignment node."""

    operator: str = required_field()
    target: AstTarget = required_field()
    value: AstExpression = required_field()


@dataclass(frozen=True)
class AstDecorator(AstNode):
    """Ast decorator node."""

    expression: AstExpression = required_field()


@dataclass(frozen=True)
class AstFunctionSignatureElement(AstNode):
    """Base node for function signature element."""


@dataclass(frozen=True)
class AstFunctionSignatureArgument(AstFunctionSignatureElement):
    """Ast function signature argument node."""

    name: str = required_field()
    default: Optional[AstExpression] = None


@dataclass(frozen=True)
class AstFunctionSignaturePositionalMarker(AstFunctionSignatureElement):
    """Ast function signature positional marker node."""


@dataclass(frozen=True)
class AstFunctionSignatureVariadicArgument(AstFunctionSignatureElement):
    """Ast function signature variadic argument node."""

    name: str = required_field()


@dataclass(frozen=True)
class AstFunctionSignatureVariadicMarker(AstFunctionSignatureElement):
    """Ast function signature variadic marker node."""


@dataclass(frozen=True)
class AstFunctionSignatureVariadicKeywordArgument(AstFunctionSignatureElement):
    """Ast function signature variadic keyword argument node."""

    name: str = required_field()


@dataclass(frozen=True)
class AstFunctionSignature(AstNode):
    """Ast function signature node."""

    decorators: AstChildren[AstDecorator] = AstChildren()
    name: str = required_field()
    arguments: AstChildren[AstFunctionSignatureElement] = AstChildren()


@dataclass(frozen=True)
class AstDeferredRoot(AstNode):
    """Ast deferred root node."""

    stream: TokenStream = required_field()


@dataclass(frozen=True)
class AstMacro(AstCommand):
    """Ast macro node."""

    def get_command_tree(self) -> JsonDict:
        tree_root: JsonDict = {"type": "root"}
        tree: JsonDict = tree_root

        for node in self.arguments:
            if isinstance(node, AstMacroLiteral):
                child = {"type": "literal"}
                tree["children"] = {node.value: child}
            elif isinstance(node, AstMacroMatchLiteral):
                child = {"type": "literal"}
                tree["children"] = {node.match.value: child}
            elif isinstance(node, AstMacroMatchArgument):
                child = {"type": "argument"}
                child["parser"] = node.match_argument_parser.get_canonical_value()
                if properties := node.match_argument_properties:
                    child["properties"] = properties.evaluate()
                tree["children"] = {node.match_identifier.value: child}
            else:
                break
            tree = child

        tree["executable"] = True

        return tree_root


@dataclass(frozen=True)
class AstMacroCall(AstCommand):
    """Ast macro call node."""


@dataclass(frozen=True)
class AstMacroLiteral(AstLiteral):
    """Ast macro literal node."""

    parser = "bolt_macro_literal"

    regex = re.compile(r"[^#:\s()]+")


@dataclass(frozen=True)
class AstMacroArgument(AstLiteral):
    """Ast macro argument node."""

    parser = "bolt_macro_argument"

    regex = re.compile(IDENTIFIER_PATTERN)


@dataclass(frozen=True)
class AstMacroMatch(AstNode):
    """Base node for macro match."""


@dataclass(frozen=True)
class AstMacroMatchLiteral(AstMacroMatch):
    """Ast macro match literal node."""

    match: AstMacroLiteral = required_field()


@dataclass(frozen=True)
class AstMacroMatchArgument(AstMacroMatch):
    """Ast macro match argument node."""

    match_identifier: AstMacroArgument = required_field()
    match_argument_parser: AstResourceLocation = required_field()
    match_argument_properties: Optional[AstJson] = None


@dataclass(frozen=True)
class AstProcMacro(AstMacro):
    """Ast proc macro node."""


@dataclass(frozen=True)
class AstProcMacroMarker(AstNode):
    """Ast proc macro marker node."""


@dataclass(frozen=True)
class AstProcMacroResult(AstNode):
    """Ast proc macro result node."""

    commands: AstChildren[AstCommand] = required_field()


@dataclass(frozen=True)
class AstClassName(AstNode):
    """Ast class name node."""

    decorators: AstChildren[AstDecorator] = AstChildren()
    value: str = required_field()


@dataclass(frozen=True)
class AstClassBases(AstNode):
    """Ast class bases node."""

    inherit: AstChildren[AstExpression] = AstChildren()


@dataclass(frozen=True)
class AstClassRoot(AstRoot):
    """Ast class root node."""


@dataclass(frozen=True)
class AstInterpolation(AstNode):
    """Ast interpolation node."""

    prefix: Optional[str] = None
    unpack: Optional[str] = None
    converter: str = required_field()
    value: AstExpression = required_field()


@dataclass(frozen=True)
class AstFromImport(AstCommand):
    """Ast from import node."""

    identifier: str = ""


@dataclass(frozen=True)
class AstImportedItem(AstNode):
    """Ast imported item node."""

    name: str = required_field()
    identifier: bool = True


@dataclass(frozen=True)
class AstImportedMacro(AstNode):
    """Ast imported macro node."""

    name: str = required_field()
    declaration: AstMacro = required_field()
