__all__ = [
    "AstModuleRoot",
    "AstExpression",
    "AstExpressionBinary",
    "AstExpressionUnary",
    "AstValue",
    "AstIdentifier",
    "AstFormatString",
    "AstFormattedLocation",
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
    "AstTypeDeclaration",
    "AstDecorator",
    "AstDocstring",
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
    "AstEscapeAnalysisRoot",
    "AstEscapeRoot",
    "AstMemo",
    "AstMemoResult",
    "AstInterpolation",
    "AstFromImport",
    "AstImportedItem",
    "AstImportedMacro",
    "AstPrelude",
]


import re
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple, Union
from uuid import UUID, uuid4

from beet.core.utils import JsonDict, extra_field, required_field
from mecha import (
    AstChildren,
    AstCommand,
    AstCommandSentinel,
    AstJson,
    AstLiteral,
    AstNode,
    AstResourceLocation,
    AstRoot,
)
from tokenstream import TokenStream

from .pattern import IDENTIFIER_PATTERN
from .semantics import Binding


@dataclass(frozen=True, slots=True)
class AstModuleRoot(AstRoot):
    """Module root ast node."""


@dataclass(frozen=True, slots=True)
class AstExpression(AstNode):
    """Base ast node for expressions."""


@dataclass(frozen=True, slots=True)
class AstExpressionBinary(AstExpression):
    """Ast expression binary node."""

    operator: str = required_field()
    left: AstExpression = required_field()
    right: AstExpression = required_field()


@dataclass(frozen=True, slots=True)
class AstExpressionUnary(AstExpression):
    """Ast expression unary node."""

    operator: str = required_field()
    value: AstExpression = required_field()


@dataclass(frozen=True, slots=True)
class AstValue(AstExpression):
    """Ast value node."""

    value: Any = required_field()

    @property
    def literal(self) -> str:
        return "..." if self.value is ... else repr(self.value)


@dataclass(frozen=True, slots=True)
class AstIdentifier(AstExpression):
    """Ast identifier node."""

    value: str = required_field()


@dataclass(frozen=True, slots=True)
class AstFormatString(AstExpression):
    """Ast format string node."""

    fmt: str = required_field()
    values: AstChildren[AstExpression] = required_field()


@dataclass(frozen=True, slots=True)
class AstFormattedLocation(AstExpression):
    """Ast formatted location node."""

    fmt: str = required_field()
    values: AstChildren[AstExpression] = required_field()


@dataclass(frozen=True, slots=True)
class AstTuple(AstExpression):
    """Ast tuple node."""

    items: AstChildren[AstExpression] = required_field()


@dataclass(frozen=True, slots=True)
class AstList(AstExpression):
    """Ast list node."""

    items: AstChildren[AstExpression] = required_field()


@dataclass(frozen=True, slots=True)
class AstDictUnquotedKey(AstValue):
    """Ast dict unquoted key node."""


@dataclass(frozen=True, slots=True)
class AstDictItem(AstNode):
    """Ast dict item node."""

    key: AstExpression = required_field()
    value: AstExpression = required_field()


@dataclass(frozen=True, slots=True)
class AstDict(AstExpression):
    """Ast dict node."""

    items: AstChildren[AstDictItem] = required_field()


@dataclass(frozen=True, slots=True)
class AstSlice(AstNode):
    """Ast slice node."""

    start: Optional[AstExpression] = None
    stop: Optional[AstExpression] = None
    step: Optional[AstExpression] = None


@dataclass(frozen=True, slots=True)
class AstUnpack(AstNode):
    """Ast unpack node."""

    type: str = required_field()
    value: AstExpression = required_field()


@dataclass(frozen=True, slots=True)
class AstKeyword(AstNode):
    """Ast keyword node."""

    name: str = required_field()
    value: AstExpression = required_field()


@dataclass(frozen=True, slots=True)
class AstAttribute(AstExpression):
    """Ast attribute node."""

    name: str = required_field()
    value: AstExpression = required_field()


@dataclass(frozen=True, slots=True)
class AstLookup(AstExpression):
    """Ast lookup node."""

    value: AstExpression = required_field()
    arguments: AstChildren[Union[AstExpression, AstSlice]] = required_field()


@dataclass(frozen=True, slots=True)
class AstCall(AstExpression):
    """Ast call node."""

    value: AstExpression = required_field()
    arguments: AstChildren[
        Union[AstExpression, AstUnpack, AstKeyword]
    ] = required_field()


@dataclass(frozen=True, slots=True)
class AstTarget(AstNode):
    """Base node for targets."""


@dataclass(frozen=True, slots=True)
class AstTargetIdentifier(AstTarget):
    """Ast target identifier node."""

    value: str = required_field()
    rebind: bool = False


@dataclass(frozen=True, slots=True)
class AstTargetUnpack(AstTarget):
    """Ast target unpack node."""

    targets: AstChildren[AstTarget] = required_field()


@dataclass(frozen=True, slots=True)
class AstTargetAttribute(AstTarget):
    """Ast target attribute node."""

    name: str = required_field()
    value: AstExpression = required_field()


@dataclass(frozen=True, slots=True)
class AstTargetItem(AstTarget):
    """Ast target item node."""

    value: AstExpression = required_field()
    arguments: AstChildren[Union[AstExpression, AstSlice]] = required_field()


@dataclass(frozen=True, slots=True)
class AstAssignment(AstNode):
    """Ast assignment node."""

    operator: str = required_field()
    target: AstTarget = required_field()
    value: AstExpression = required_field()
    type_annotation: Optional[AstExpression] = None


@dataclass(frozen=True, slots=True)
class AstTypeDeclaration(AstNode):
    """Ast type declaration node."""

    identifier: AstTargetIdentifier = required_field()
    type_annotation: AstExpression = required_field()


@dataclass(frozen=True, slots=True)
class AstDecorator(AstNode):
    """Ast decorator node."""

    expression: AstExpression = required_field()


@dataclass(frozen=True, slots=True)
class AstDocstring(AstCommandSentinel):
    """Ast docstring node."""


@dataclass(frozen=True, slots=True)
class AstFunctionSignatureElement(AstNode):
    """Base node for function signature element."""


@dataclass(frozen=True, slots=True)
class AstFunctionSignatureArgument(AstFunctionSignatureElement):
    """Ast function signature argument node."""

    name: str = required_field()
    type_annotation: Optional[AstExpression] = None
    default: Optional[AstExpression] = None


@dataclass(frozen=True, slots=True)
class AstFunctionSignaturePositionalMarker(AstFunctionSignatureElement):
    """Ast function signature positional marker node."""


@dataclass(frozen=True, slots=True)
class AstFunctionSignatureVariadicArgument(AstFunctionSignatureElement):
    """Ast function signature variadic argument node."""

    name: str = required_field()
    type_annotation: Optional[AstExpression] = None


@dataclass(frozen=True, slots=True)
class AstFunctionSignatureVariadicMarker(AstFunctionSignatureElement):
    """Ast function signature variadic marker node."""


@dataclass(frozen=True, slots=True)
class AstFunctionSignatureVariadicKeywordArgument(AstFunctionSignatureElement):
    """Ast function signature variadic keyword argument node."""

    name: str = required_field()
    type_annotation: Optional[AstExpression] = None


@dataclass(frozen=True, slots=True)
class AstFunctionSignature(AstNode):
    """Ast function signature node."""

    decorators: AstChildren[AstDecorator] = AstChildren()
    name: str = required_field()
    arguments: AstChildren[AstFunctionSignatureElement] = AstChildren()
    return_type_annotation: Optional[AstExpression] = None


@dataclass(frozen=True, slots=True)
class AstDeferredRoot(AstNode):
    """Ast deferred root node."""

    stream: TokenStream = required_field()


@dataclass(frozen=True, slots=True)
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
                if node.is_subcommand():
                    tree["redirect"] = (
                        node.match_argument_properties.evaluate().get("redirect", [])
                        if node.match_argument_properties
                        else []
                    )
                    return tree_root
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


@dataclass(frozen=True, slots=True)
class AstMacroCall(AstCommand):
    """Ast macro call node."""


@dataclass(frozen=True, slots=True)
class AstMacroLiteral(AstLiteral):
    """Ast macro literal node."""

    parser = "bolt_macro_literal"

    regex = re.compile(r"[^#:\s()]+")


@dataclass(frozen=True, slots=True)
class AstMacroArgument(AstLiteral):
    """Ast macro argument node."""

    parser = "bolt_macro_argument"

    regex = re.compile(IDENTIFIER_PATTERN)


@dataclass(frozen=True, slots=True)
class AstMacroMatch(AstNode):
    """Base node for macro match."""


@dataclass(frozen=True, slots=True)
class AstMacroMatchLiteral(AstMacroMatch):
    """Ast macro match literal node."""

    match: AstMacroLiteral = required_field()


@dataclass(frozen=True, slots=True)
class AstMacroMatchArgument(AstMacroMatch):
    """Ast macro match argument node."""

    match_identifier: AstMacroArgument = required_field()
    match_argument_parser: AstResourceLocation = required_field()
    match_argument_properties: Optional[AstJson] = None

    def is_subcommand(self) -> bool:
        return (
            not self.match_argument_parser.namespace
            and self.match_argument_parser.path == "subcommand"
        )


@dataclass(frozen=True, slots=True)
class AstProcMacro(AstMacro):
    """Ast proc macro node."""


@dataclass(frozen=True, slots=True)
class AstProcMacroMarker(AstNode):
    """Ast proc macro marker node."""


@dataclass(frozen=True, slots=True)
class AstProcMacroResult(AstNode):
    """Ast proc macro result node."""

    commands: AstChildren[AstCommand] = required_field()


@dataclass(frozen=True, slots=True)
class AstClassName(AstNode):
    """Ast class name node."""

    decorators: AstChildren[AstDecorator] = AstChildren()
    value: str = required_field()


@dataclass(frozen=True, slots=True)
class AstClassBases(AstNode):
    """Ast class bases node."""

    inherit: AstChildren[AstExpression] = AstChildren()


@dataclass(frozen=True, slots=True)
class AstClassRoot(AstRoot):
    """Ast class root node."""


@dataclass(frozen=True, slots=True)
class AstEscapeAnalysisRoot(AstRoot):
    """Ast escape analysis root node."""

    refcount_snapshots: List[Tuple[str, Binding, int]] = extra_field(
        default_factory=list
    )


@dataclass(frozen=True, slots=True)
class AstEscapeRoot(AstRoot):
    """Ast escape root node."""

    identifiers: Tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class AstMemo(AstCommand):
    """Ast memo node."""

    persistent_id: UUID = extra_field(default_factory=uuid4)


@dataclass(frozen=True, slots=True)
class AstMemoResult(AstCommandSentinel):
    """Ast memo result node."""

    serialized: str = ""

    compile_hints = {"skip_execute_inline_single_command": True}


@dataclass(frozen=True, slots=True)
class AstInterpolation(AstNode):
    """Ast interpolation node."""

    prefix: Optional[str] = None
    unpack: Optional[str] = None
    converter: str = required_field()
    value: AstExpression = required_field()


@dataclass(frozen=True, slots=True)
class AstFromImport(AstCommand):
    """Ast from import node."""

    identifier: str = ""


@dataclass(frozen=True, slots=True)
class AstImportedItem(AstNode):
    """Ast imported item node."""

    name: str = required_field()
    identifier: bool = True


@dataclass(frozen=True, slots=True)
class AstImportedMacro(AstNode):
    """Ast imported macro node."""

    name: str = required_field()
    declaration: AstMacro = required_field()


@dataclass(frozen=True, slots=True)
class AstPrelude(AstFromImport):
    """Ast prelude node."""

    @classmethod
    def placeholder(cls, resource_location: str) -> "AstPrelude":
        return cls(
            arguments=AstChildren(
                [
                    AstResourceLocation.from_value(resource_location),
                    AstImportedItem(name="_bolt_placeholder"),
                ]
            )
        )
