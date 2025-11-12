__all__ = [
    "McdocNode",
    "McdocChildren",
    "McdocDocComment",
    "McdocPrelim",
    "McdocBoolean",
    "McdocInteger",
    "McdocFloat",
    "McdocTypedNumber",
    "McdocIntegerRange",
    "McdocFloatRange",
    "McdocString",
    "McdocResourceLocation",
    "McdocIdentifier",
    "McdocPath",
    "McdocPathSegment",
    "McdocSuper",
    "McdocType",
    "McDocUnattributedType",
    "McdocTypeModifier",
    "McdocAnyType",
    "McdocBooleanType",
    "McdocStringType",
    "McdocNumericType",
    "McdocPrimitiveArrayType",
    "McdocListType",
    "McdocTupleType",
    "McdocEnum",
    "McdocEnumField",
    "McdocEnumValue",
    "McdocStruct",
    "McdocStructField",
    "McdocStructKey",
    "McdocDynamicKey",
    "McdocSpread",
    "McdocReferenceType",
    "McdocDispatcherType",
    "McdocUnionType",
    "McdocIndexBody",
    "McdocIndex",
    "McdocStaticIndex",
    "McdocFallbackIndexKey",
    "McdocNoneIndexKey",
    "McdocUnknownIndexKey",
    "McdocDynamicIndex",
    "McdocAccessor",
    "McdocKeyIndexKey",
    "McdocParentIndexKey",
    "McdocTypeArgBlock",
    "Mcdoc",
    "McdocItem",
    "McdocTypeAlias",
    "McdocUseStatement",
    "McdocDispatchStatement",
    "McdocAttribute",
    "McdocAttributeValue",
    "McdocAttributeTree",
    "McdocAttributeTreeNamedValue",
    "McdocAttributeTreeName",
    "parse_mcdoc",
]

from contextlib import contextmanager
from dataclasses import dataclass, replace
from typing import (
    Callable,
    Iterator,
    List,
    Literal,
    Optional,
    Set,
    TypeAlias,
    TypeVar,
    Union,
)

from beet.core.utils import required_field
from tokenstream import InvalidSyntax, TokenPattern, TokenStream, set_location

from mecha import AbstractChildren, AbstractNode
from mecha.utils import QuoteHelper

McdocNodeType = TypeVar("McdocNodeType", bound="McdocNode", covariant=True)

PATTERN_INTEGER: str = r"[-+]?[1-9][0-9]*|0"
PATTERN_FLOAT: str = r"[-+]?(?:[0-9]*\.[0-9]+|[0-9]+)(?:[eE][-+]?[0-9]+)?"
PATTERN_TYPED_NUMBER: str = rf"{PATTERN_FLOAT}[bBdDfFlLsS]?"
PATTERN_RANGE_DELIMITER: str = r"<?\.\.<?"
PATTERN_INTEGER_RANGE: str = rf"(?:{PATTERN_INTEGER})(?:{PATTERN_RANGE_DELIMITER})(?:{PATTERN_INTEGER})?|(?:{PATTERN_RANGE_DELIMITER})?(?:{PATTERN_INTEGER})"
PATTERN_FLOAT_RANGE: str = rf"(?:{PATTERN_FLOAT})(?:{PATTERN_RANGE_DELIMITER})(?:{PATTERN_FLOAT})?|(?:{PATTERN_RANGE_DELIMITER})?(?:{PATTERN_FLOAT})"
PATTERN_STRING: str = r'"(?:[^"\\]|\\[bfnrt\\"])*"'
PATTERN_RESOURCE_LOCATION: str = r"[a-z0-9_.-]*:(?!:)[a-z0-9_.-]*(?:/[a-z0-9_.-]*)*"
PATTERN_IDENTIFIER: str = r"[a-zA-Z0-9_]+"


RESERVED_WORDS: Set[str] = {
    "any",
    "boolean",
    "byte",
    "double",
    "enum",
    "false",
    "float",
    "int",
    "long",
    "short",
    "string",
    "struct",
    "super",
    "true",
}

MCDOC_QUOTE_HELPER: QuoteHelper = QuoteHelper(
    escape_sequences={
        r"\"": '"',
        r"\\": "\\",
        r"\b": "\b",
        r"\f": "\f",
        r"\r": "\r",
        r"\n": "\n",
        r"\t": "\t",
    }
)


class McdocNode(AbstractNode):
    """Base class for mcdoc nodes."""

    def __iter__(self) -> Iterator["McdocNode"]:
        return super().__iter__()  # type: ignore

    def walk(self) -> Iterator["McdocNode"]:
        return super().walk()  # type: ignore


class McdocChildren(AbstractChildren[McdocNodeType]):
    """Specialized tuple subclass for holding multiple child mcdoc nodes."""


@dataclass(frozen=True, slots=True)
class McdocDocComment(McdocNode):
    """Mcdoc doc comment node."""

    text: str = required_field()


@dataclass(frozen=True, slots=True)
class McdocPrelim(McdocNode):
    """Mcdoc prelim node."""

    doc_comments: McdocChildren[McdocDocComment] = required_field()
    attributes: McdocChildren["McdocAttribute"] = required_field()


@dataclass(frozen=True, slots=True)
class McdocBoolean(McdocNode):
    """Mcdoc boolean node."""

    value: bool = required_field()


@dataclass(frozen=True, slots=True)
class McdocInteger(McdocNode):
    """Mcdoc integer node."""

    value: int = required_field()


@dataclass(frozen=True, slots=True)
class McdocFloat(McdocNode):
    """Mcdoc float node."""

    value: float = required_field()


@dataclass(frozen=True, slots=True)
class McdocTypedNumber(McdocNode):
    """Mcdoc typed number node."""

    value: Union[int, float] = required_field()
    type: Literal["byte", "short", "int", "long", "float", "double"] = required_field()


@dataclass(frozen=True, slots=True)
class McdocIntegerRange(McdocNode):
    """Mcdoc integer range node."""

    left: Optional[int] = required_field()
    delimiter: Literal["..", "..<", "<..", "<..<"] = required_field()
    right: Optional[int] = required_field()


@dataclass(frozen=True, slots=True)
class McdocFloatRange(McdocNode):
    """Mcdoc float range node."""

    left: Optional[float] = required_field()
    delimiter: Literal["..", "..<", "<..", "<..<"] = required_field()
    right: Optional[float] = required_field()


@dataclass(frozen=True, slots=True)
class McdocString(McdocNode):
    """Mcdoc string node."""

    value: str = required_field()


@dataclass(frozen=True, slots=True)
class McdocResourceLocation(McdocNode):
    """Mcdoc resource location node."""

    value: str = required_field()


@dataclass(frozen=True, slots=True)
class McdocIdentifier(McdocNode):
    """Mcdoc identifier node."""

    name: str = required_field()


@dataclass(frozen=True, slots=True)
class McdocPath(McdocNode):
    """Mcdoc path node."""

    absolute: bool = required_field()
    segments: McdocChildren["McdocPathSegment"] = required_field()


McdocPathSegment: TypeAlias = Union[McdocIdentifier, "McdocSuper"]


@dataclass(frozen=True, slots=True)
class McdocSuper(McdocNode):
    """Mcdoc super node."""


@dataclass(frozen=True, slots=True)
class McdocType(McdocNode):
    """Mcdoc type node."""

    attributes: McdocChildren["McdocAttribute"] = required_field()
    unattributed_type: "McDocUnattributedType" = required_field()
    modifiers: McdocChildren["McdocTypeModifier"] = required_field()


McDocUnattributedType: TypeAlias = Union[
    "McdocAnyType",
    "McdocBooleanType",
    "McdocStringType",
    McdocBoolean,
    McdocString,
    McdocTypedNumber,
    "McdocNumericType",
    "McdocPrimitiveArrayType",
    "McdocListType",
    "McdocTupleType",
    "McdocEnum",
    "McdocStruct",
    "McdocReferenceType",
    "McdocDispatcherType",
    "McdocUnionType",
]

McdocTypeModifier: TypeAlias = Union["McdocIndexBody", "McdocTypeArgBlock"]


@dataclass(frozen=True, slots=True)
class McdocAnyType(McdocNode):
    """Mcdoc any type node."""


@dataclass(frozen=True, slots=True)
class McdocBooleanType(McdocNode):
    """Mcdoc boolean type node."""


@dataclass(frozen=True, slots=True)
class McdocStringType(McdocNode):
    """Mcdoc string type node."""

    length: Optional[McdocIntegerRange] = None


@dataclass(frozen=True, slots=True)
class McdocNumericType(McdocNode):
    """Mcdoc numeric type node."""

    name: Literal["byte", "short", "int", "long", "float", "double"] = required_field()
    constraint: Optional[McdocIntegerRange] = None


@dataclass(frozen=True, slots=True)
class McdocPrimitiveArrayType(McdocNode):
    """Mcdoc primitive array type node."""

    name: Literal["byte", "int", "long"] = required_field()
    constraint: Optional[McdocIntegerRange] = None
    length: Optional[McdocIntegerRange] = None


@dataclass(frozen=True, slots=True)
class McdocListType(McdocNode):
    """Mcdoc list type node."""

    element: McdocType = required_field()
    length: Optional[McdocIntegerRange] = None


@dataclass(frozen=True, slots=True)
class McdocTupleType(McdocNode):
    """Mcdoc tuple type node."""

    elements: McdocChildren[McdocType] = required_field()


@dataclass(frozen=True, slots=True)
class McdocEnum(McdocNode):
    """Mcdoc enum node."""

    prelim: McdocPrelim = required_field()
    type: Literal[
        "byte",
        "short",
        "int",
        "long",
        "string",
        "float",
        "double",
    ] = required_field()
    identifier: Optional[McdocIdentifier] = required_field()
    fields: McdocChildren["McdocEnumField"] = required_field()


@dataclass(frozen=True, slots=True)
class McdocEnumField(McdocNode):
    """Mcdoc enum field node."""

    prelim: McdocPrelim = required_field()
    identifier: McdocIdentifier = required_field()
    value: "McdocEnumValue" = required_field()


McdocEnumValue: TypeAlias = Union[McdocTypedNumber, McdocString]


@dataclass(frozen=True, slots=True)
class McdocStruct(McdocNode):
    """Mcdoc struct node."""

    prelim: McdocPrelim = required_field()
    identifier: Optional[McdocIdentifier] = required_field()
    fields: McdocChildren[Union["McdocStructField", "McdocSpread"]] = required_field()


@dataclass(frozen=True, slots=True)
class McdocStructField(McdocNode):
    """Mcdoc struct field node."""

    prelim: McdocPrelim = required_field()
    key: "McdocStructKey" = required_field()
    optional: bool = required_field()
    type: McdocType = required_field()


McdocStructKey: TypeAlias = Union[McdocString, McdocIdentifier, "McdocDynamicKey"]


@dataclass(frozen=True, slots=True)
class McdocDynamicKey(McdocNode):
    """Mcdoc dynamic key node."""

    type: McdocType = required_field()


@dataclass(frozen=True, slots=True)
class McdocSpread(McdocNode):
    """Mcdoc spread node."""

    attributes: McdocChildren["McdocAttribute"] = required_field()
    type: McdocType = required_field()


@dataclass(frozen=True, slots=True)
class McdocReferenceType(McdocNode):
    """Mcdoc reference type node."""

    path: McdocPath = required_field()


@dataclass(frozen=True, slots=True)
class McdocDispatcherType(McdocNode):
    """Mcdoc dispatcher type node."""

    resource_location: McdocResourceLocation = required_field()
    indices: McdocChildren["McdocIndex"] = required_field()


@dataclass(frozen=True, slots=True)
class McdocUnionType(McdocNode):
    """Mcdoc union type node."""

    types: McdocChildren[McdocType] = required_field()


@dataclass(frozen=True, slots=True)
class McdocIndexBody(McdocNode):
    """Mcdoc index body node."""

    indices: McdocChildren["McdocIndex"] = required_field()


McdocIndex: TypeAlias = Union[
    "McdocStaticIndex",
    "McdocDynamicIndex",
]

McdocStaticIndex: TypeAlias = Union[
    "McdocFallbackIndexKey",
    "McdocNoneIndexKey",
    "McdocUnknownIndexKey",
    McdocIdentifier,
    McdocString,
    McdocResourceLocation,
]


@dataclass(frozen=True, slots=True)
class McdocFallbackIndexKey(McdocNode):
    """Mcdoc %fallback index key node."""


@dataclass(frozen=True, slots=True)
class McdocNoneIndexKey(McdocNode):
    """Mcdoc %none index key node."""


@dataclass(frozen=True, slots=True)
class McdocUnknownIndexKey(McdocNode):
    """Mcdoc %unknown index key node."""


@dataclass(frozen=True, slots=True)
class McdocDynamicIndex(McdocNode):
    """Mcdoc dynamic index node."""

    accessors: McdocChildren["McdocAccessor"] = required_field()


McdocAccessor: TypeAlias = Union[
    "McdocKeyIndexKey",
    "McdocParentIndexKey",
    McdocIdentifier,
    McdocString,
]


@dataclass(frozen=True, slots=True)
class McdocKeyIndexKey(McdocNode):
    """Mcdoc %key index key node."""


@dataclass(frozen=True, slots=True)
class McdocParentIndexKey(McdocNode):
    """Mcdoc %parent index key node."""


@dataclass(frozen=True, slots=True)
class McdocTypeArgBlock(McdocNode):
    """Mcdoc type arg block node."""

    arguments: McdocChildren[McdocType] = required_field()


@dataclass(frozen=True, slots=True)
class Mcdoc(McdocNode):
    """Mcdoc node."""

    items: McdocChildren["McdocItem"] = required_field()


McdocItem: TypeAlias = Union[
    McdocStruct,
    McdocEnum,
    "McdocTypeAlias",
    "McdocUseStatement",
    "McdocDispatchStatement",
]


@dataclass(frozen=True, slots=True)
class McdocTypeAlias(McdocNode):
    """Mcdoc type alias node."""

    prelim: McdocPrelim = required_field()
    identifier: McdocIdentifier = required_field()
    parameters: McdocChildren[McdocIdentifier] = required_field()
    type: McdocType = required_field()


@dataclass(frozen=True, slots=True)
class McdocUseStatement(McdocNode):
    """Mcdoc use statement node."""

    path: McdocPath = required_field()
    alias: Optional[McdocIdentifier] = None


@dataclass(frozen=True, slots=True)
class McdocDispatchStatement(McdocNode):
    """Mcdoc dispatch statement node."""

    attributes: McdocChildren["McdocAttribute"] = required_field()
    resource_location: McdocResourceLocation = required_field()
    indices: McdocChildren["McdocStaticIndex"] = required_field()
    parameters: McdocChildren[McdocIdentifier] = required_field()
    type: McdocType = required_field()


@dataclass(frozen=True, slots=True)
class McdocAttribute(McdocNode):
    """Mcdoc attribute node."""

    identifier: McdocIdentifier = required_field()
    value: Optional["McdocAttributeValue"] = None


McdocAttributeValue: TypeAlias = Union[McdocType, "McdocAttributeTree"]


@dataclass(frozen=True, slots=True)
class McdocAttributeTree(McdocNode):
    """Mcdoc attribute tree node."""

    flavor: Literal["brace", "bracket", "curly"] = required_field()
    positional_values: McdocChildren[McdocAttributeValue] = required_field()
    named_values: McdocChildren["McdocAttributeTreeNamedValue"] = required_field()


@dataclass(frozen=True, slots=True)
class McdocAttributeTreeNamedValue(McdocNode):
    """Mcdoc attribute tree named value node."""

    name: "McdocAttributeTreeName" = required_field()
    value: McdocAttributeValue = required_field()


McdocAttributeTreeName: TypeAlias = Union[McdocIdentifier, McdocString]


@contextmanager
def ignore_comments(stream: TokenStream):
    with stream.syntax(comment=r"//(?!/)[^\n]*\n?"), stream.ignore("comment"):
        yield


def parse_prelim(stream: TokenStream) -> McdocPrelim:
    with stream.syntax(doc_comment=r"///[^\n]*\n?"):
        with stream.intercept("comment"):
            while stream.get("comment"):
                pass

            start = stream.peek()
            doc_comments: List[McdocDocComment] = []

            for token in stream.collect("doc_comment"):
                node = McdocDocComment(text=token.value)
                doc_comments.append(set_location(node, token))

        attributes = parse_attributes(stream)

        node = McdocPrelim(
            doc_comments=McdocChildren(doc_comments),
            attributes=attributes,
        )
        return set_location(
            node,
            start,
            stream.current if doc_comments or attributes else start,
        )


def parse_integer(stream: TokenStream) -> McdocInteger:
    with stream.syntax(integer=PATTERN_INTEGER):
        token = stream.expect("integer")
        node = McdocInteger(value=int(token.value))
        return set_location(node, token)


def parse_float(stream: TokenStream) -> McdocFloat:
    with stream.syntax(float=PATTERN_FLOAT):
        token = stream.expect("float")
        node = McdocFloat(value=float(token.value))
        return set_location(node, token)


def parse_typed_number(stream: TokenStream) -> McdocTypedNumber:
    with stream.syntax(typed_number=PATTERN_TYPED_NUMBER):
        token = stream.expect("typed_number")
        normalized = token.value.lower()

        if normalized.endswith(("b", "s", "l")):
            if "." in normalized:
                value = int(float(normalized[:-1]))
            else:
                value = int(normalized[:-1])
            suffix = normalized[-1]
            type = "byte" if suffix == "b" else "short" if suffix == "s" else "long"
        elif normalized.endswith(("f", "d")):
            value = float(normalized[:-1])
            suffix = normalized[-1]
            type = "float" if suffix == "f" else "double"
        elif "." in normalized:
            value = float(normalized)
            type = "double"
        else:
            value = int(normalized)
            type = "int"

        node = McdocTypedNumber(value=value, type=type)
        return set_location(node, token)


def parse_integer_range(stream: TokenStream) -> McdocIntegerRange:
    with stream.syntax(integer_range=PATTERN_INTEGER_RANGE):
        token = stream.expect("integer_range")
        before, delimiter, after = token.value.partition("..")

        if delimiter:
            left = int(before.removesuffix("<")) if before else None
            right = int(after.removeprefix("<")) if after else None
        else:
            left = int(before)
            delimiter = ".."
            right = left

        node = McdocIntegerRange(left=left, delimiter=delimiter, right=right)  # type: ignore
        return set_location(node, token)


def parse_float_range(stream: TokenStream) -> McdocFloatRange:
    with stream.syntax(float_range=PATTERN_FLOAT_RANGE):
        token = stream.expect("float_range")
        before, delimiter, after = token.value.partition("..")

        if delimiter:
            left = float(before.removesuffix("<")) if before else None
            right = float(after.removeprefix("<")) if after else None
        else:
            left = float(before)
            delimiter = ".."
            right = left

        node = McdocFloatRange(left=left, delimiter=delimiter, right=right)  # type: ignore
        return set_location(node, token)


def parse_string(stream: TokenStream) -> McdocString:
    with stream.syntax(string=PATTERN_STRING):
        token = stream.expect("string")
        value = MCDOC_QUOTE_HELPER.unquote_string(token)
        node = McdocString(value=value)
        return set_location(node, token)


def parse_resource_location(stream: TokenStream) -> McdocResourceLocation:
    with stream.syntax(resource_location=PATTERN_RESOURCE_LOCATION):
        token = stream.expect("resource_location")
        node = McdocResourceLocation(value=token.value)
        return set_location(node, token)


def parse_identifier(stream: TokenStream) -> McdocIdentifier:
    with stream.syntax(identifier=PATTERN_IDENTIFIER):
        token = stream.expect("identifier")
        name = token.value

        if name in RESERVED_WORDS:
            exc = InvalidSyntax(f'Can\'t use reserved word "{name}" as an identifier.')
            raise set_location(exc, token)

        node = McdocIdentifier(name=name)
        return set_location(node, token)


def parse_path(stream: TokenStream) -> McdocPath:
    with stream.syntax(delimiter=r"::", super=r"super\b"):
        start = stream.get("delimiter")

        absolute = bool(start)
        segments: List[McdocPathSegment] = []

        while True:
            if token := stream.get("super"):
                node = set_location(McdocSuper(), token)
            else:
                node = parse_identifier(stream)
            segments.append(node)
            if not stream.get("delimiter"):
                break

        node = McdocPath(absolute=absolute, segments=McdocChildren(segments))
        return set_location(node, start or segments[0], segments[-1])


def parse_type(stream: TokenStream) -> McdocType:
    with stream.syntax(bracket=r"\[|\]", angle=r"<|>"):
        attributes = parse_attributes(stream)

        unattributed_type: McDocUnattributedType = parse_unattributed_type(stream)
        modifiers: List[McdocTypeModifier] = []

        for open_bracket, open_angle in stream.collect(
            ("bracket", "["),
            ("angle", "<"),
        ):
            if open_bracket:
                indices: List[McdocIndex] = []
                close_bracket = expect_sequence(
                    stream,
                    indices,
                    lambda s: choose_alternative(
                        s, parse_dynamic_index, parse_static_index
                    ),
                    until=("bracket", "]"),
                )
                if not indices:
                    exc = InvalidSyntax("Expected at least one index.")
                    raise set_location(exc, open_bracket, close_bracket)
                node = McdocIndexBody(indices=McdocChildren(indices))
                modifiers.append(set_location(node, open_bracket, close_bracket))

            elif open_angle:
                arguments: List[McdocType] = []
                close_angle = expect_sequence(
                    stream,
                    arguments,
                    parse_type,
                    until=("angle", ">"),
                )
                node = McdocTypeArgBlock(arguments=McdocChildren(arguments))
                modifiers.append(set_location(node, open_angle, close_angle))

    node = McdocType(
        attributes=attributes,
        unattributed_type=unattributed_type,
        modifiers=McdocChildren(modifiers),
    )
    return set_location(
        node,
        attributes[0] if attributes else unattributed_type,
        modifiers[-1] if modifiers else unattributed_type,
    )


def parse_unattributed_type(stream: TokenStream) -> McDocUnattributedType:
    with stream.syntax(
        any=r"any\b",
        boolean=r"boolean\b",
        string=r"string\b",
        constraint=r"@",
        true=r"true\b",
        false=r"false\b",
        byte=r"byte\b",
        short=r"short\b",
        int=r"int\b",
        long=r"long\b",
        float=r"float\b",
        double=r"double\b",
        array=r"\[\]",
        bracket=r"\[|\]",
        comma=r",",
    ):
        token = stream.get(
            "any",
            "boolean",
            "string",
            "true",
            "false",
            "byte",
            "short",
            "int",
            "long",
            "float",
            "double",
            ("bracket", "["),
        )

        if not token:
            return choose_alternative(
                stream,
                parse_string,
                parse_typed_number,
                parse_enum,
                parse_struct,
                parse_dispatcher_type,
                parse_reference_type,
                parse_union_type,
            )

        if token.match("any"):
            return set_location(McdocAnyType(), token)
        elif token.match("boolean"):
            return set_location(McdocBooleanType(), token)
        elif token.match("string"):
            length = parse_integer_range(stream) if stream.get("constraint") else None
            node = McdocStringType(length=length)
            return set_location(node, token, node.length)
        elif token.match("true"):
            return set_location(McdocBoolean(value=True), token)
        elif token.match("false"):
            return set_location(McdocBoolean(value=False), token)

        if token.type in ("byte", "short", "int", "long", "float", "double"):
            node = set_location(McdocNumericType(name=token.type), token)

            if stream.get("constraint"):
                node = replace(node, constraint=parse_integer_range(stream))
                node = set_location(node, node, node.constraint)

            if node.name in ("byte", "int", "long"):
                if array := stream.get("array"):
                    length = (
                        parse_integer_range(stream)
                        if stream.get("constraint")
                        else None
                    )
                    node = McdocPrimitiveArrayType(
                        name=node.name,
                        constraint=node.constraint,
                        length=length,
                    )
                    node = set_location(node, node.name, length or array)

            return node

        element = parse_type(stream)

        if close_bracket := stream.get(("bracket", "]")):
            length = None
            if stream.get("constraint"):
                length = parse_integer_range(stream)
            if length == McdocIntegerRange(left=1, delimiter="..", right=1):
                node = McdocTupleType(elements=McdocChildren([element]))
            else:
                node = McdocListType(element=element, length=length)
            return set_location(node, token, length or close_bracket)

        stream.expect("comma")

        elements = [element]
        close_bracket = expect_sequence(
            stream,
            elements,
            parse_type,
            until=("bracket", "]"),
        )
        node = McdocTupleType(elements=McdocChildren(elements))
        return set_location(node, token, close_bracket)


def parse_enum(stream: TokenStream) -> McdocEnum:
    with stream.syntax(
        enum=r"enum\b",
        brace=r"\(|\)",
        byte=r"byte\b",
        short=r"short\b",
        int=r"int\b",
        long=r"long\b",
        string=r"string\b",
        float=r"float\b",
        double=r"double\b",
        curly=r"\{|\}",
    ):
        prelim = parse_prelim(stream)

        stream.expect("enum")
        stream.expect(("brace", "("))
        type = stream.expect_any(
            "byte",
            "short",
            "int",
            "long",
            "string",
            "float",
            "double",
        )
        stream.expect(("brace", ")"))

        identifier = None
        with stream.alternative():
            identifier = parse_identifier(stream)

        fields: List[McdocEnumField] = []
        stream.expect(("curly", "{"))
        close_curly = expect_sequence(
            stream,
            fields,
            parse_enum_field,
            until=("curly", "}"),
        )

        node = McdocEnum(
            prelim=prelim,
            type=type.value,  # type: ignore
            identifier=identifier,
            fields=McdocChildren(fields),
        )
        return set_location(node, prelim, close_curly)


def parse_enum_field(stream: TokenStream) -> McdocEnumField:
    with stream.syntax(equal=r"="):
        prelim = parse_prelim(stream)

        identifier = parse_identifier(stream)
        stream.expect("equal")
        value = choose_alternative(stream, parse_string, parse_typed_number)

        node = McdocEnumField(prelim=prelim, identifier=identifier, value=value)
        return set_location(node, prelim, value)


def parse_struct(stream: TokenStream) -> McdocStruct:
    with stream.syntax(struct=r"struct\b", curly=r"\{|\}"):
        prelim = parse_prelim(stream)

        stream.expect("struct")

        identifier = None
        with stream.alternative():
            identifier = parse_identifier(stream)

        fields: List[Union[McdocStructField, McdocSpread]] = []
        stream.expect(("curly", "{"))
        close_curly = expect_sequence(
            stream,
            fields,
            lambda s: choose_alternative(s, parse_struct_field, parse_spread),
            until=("curly", "}"),
        )

        node = McdocStruct(
            prelim=prelim,
            identifier=identifier,
            fields=McdocChildren(fields),
        )
        return set_location(node, prelim, close_curly)


def parse_struct_field(stream: TokenStream) -> McdocStructField:
    with stream.syntax(optional=r"\?", colon=r":", bracket=r"\[|\]"):
        prelim = parse_prelim(stream)

        if open_bracket := stream.get(("bracket", "[")):
            type = parse_type(stream)
            close_bracket = stream.expect(("bracket", "]"))
            key = McdocDynamicKey(type=type)
            key = set_location(key, open_bracket, close_bracket)
        else:
            key = choose_alternative(stream, parse_string, parse_identifier)

        optional = bool(stream.get("optional"))
        stream.expect("colon")

        type = parse_type(stream)

        node = McdocStructField(prelim=prelim, key=key, optional=optional, type=type)
        return set_location(node, prelim, type)


def parse_spread(stream: TokenStream) -> McdocSpread:
    with stream.syntax(spread=r"\.\.\."):
        attributes = parse_attributes(stream)
        token = stream.expect("spread")
        type = parse_type(stream)
        node = McdocSpread(attributes=attributes, type=type)
        return set_location(node, attributes[0] if attributes else token, type)


def parse_reference_type(stream: TokenStream) -> McdocReferenceType:
    path = parse_path(stream)
    node = McdocReferenceType(path=path)
    return set_location(node, path)


def parse_dispatcher_type(stream: TokenStream) -> McdocDispatcherType:
    with stream.syntax(bracket=r"\[|\]"):
        resource_location = parse_resource_location(stream)

        open_bracket = stream.expect(("bracket", "["))
        indices: List[McdocIndex] = []
        close_bracket = expect_sequence(
            stream,
            indices,
            lambda s: choose_alternative(s, parse_dynamic_index, parse_static_index),
            until=("bracket", "]"),
        )

        if not indices:
            exc = InvalidSyntax("Expected at least one index.")
            raise set_location(exc, open_bracket, close_bracket)

        node = McdocDispatcherType(
            resource_location=resource_location,
            indices=McdocChildren(indices),
        )
        return set_location(node, resource_location, close_bracket)


def parse_union_type(stream: TokenStream) -> McdocUnionType:
    with stream.syntax(brace=r"\(|\)", pipe=r"\|"):
        open_brace = stream.expect(("brace", "("))
        types: List[McdocType] = []
        close_brace = expect_sequence(
            stream,
            types,
            parse_type,
            until=("brace", ")"),
            separator=r"\|",
        )
        node = McdocUnionType(types=McdocChildren(types))
        return set_location(node, open_brace, close_brace)


def parse_static_index(stream: TokenStream) -> McdocStaticIndex:
    with stream.syntax(fallback=r"%fallback\b", none=r"%none\b", unknown=r"%unknown\b"):
        with stream.alternative():
            fallback, none, unknown = stream.expect("fallback", "none", "unknown")
            if fallback:
                return set_location(McdocFallbackIndexKey(), fallback)
            elif none:
                return set_location(McdocNoneIndexKey(), none)
            elif unknown:
                return set_location(McdocUnknownIndexKey(), unknown)

        return choose_alternative(
            stream,
            parse_string,
            parse_resource_location,
            parse_identifier,
        )


def parse_dynamic_index(stream: TokenStream) -> McdocDynamicIndex:
    with stream.syntax(bracket=r"\[|\]", dot=r"\."):
        open_bracket = stream.expect(("bracket", "["))

        accessors: List[McdocAccessor] = [parse_accessor(stream)]
        for _ in stream.collect("dot"):
            accessors.append(parse_accessor(stream))

        close_bracket = stream.expect(("bracket", "]"))

        node = McdocDynamicIndex(accessors=McdocChildren(accessors))
        return set_location(node, open_bracket, close_bracket)


def parse_accessor(stream: TokenStream) -> McdocAccessor:
    with stream.syntax(key=r"%key\b", parent=r"%parent\b"):
        with stream.alternative():
            key, parent = stream.expect("key", "parent")
            if key:
                return set_location(McdocKeyIndexKey(), key)
            elif parent:
                return set_location(McdocParentIndexKey(), parent)

        return choose_alternative(
            stream,
            parse_string,
            parse_identifier,
        )


def parse_mcdoc(stream: TokenStream) -> Mcdoc:
    with ignore_comments(stream):
        items: List[McdocItem] = []

        while stream.peek():
            item = choose_alternative(
                stream,
                parse_struct,
                parse_enum,
                parse_type_alias,
                parse_use_statement,
                parse_dispatch_statement,
            )
            items.append(item)

        node = Mcdoc(items=McdocChildren(items))
        return set_location(
            node,
            items[0] if items else stream.current,
            items[-1] if items else stream.current,
        )


def parse_type_alias(stream: TokenStream) -> McdocTypeAlias:
    with stream.syntax(type=r"type\b", angle=r"<|>", equal=r"="):
        prelim = parse_prelim(stream)

        stream.expect("type")
        identifier = parse_identifier(stream)

        parameters: List[McdocIdentifier] = []
        if stream.get(("angle", "<")):
            expect_sequence(
                stream,
                parameters,
                parse_identifier,
                until=("angle", ">"),
            )

        stream.expect("equal")

        type = parse_type(stream)

        node = McdocTypeAlias(
            prelim=prelim,
            identifier=identifier,
            parameters=McdocChildren(parameters),
            type=type,
        )
        return set_location(node, prelim, type)


def parse_use_statement(stream: TokenStream) -> McdocUseStatement:
    with stream.syntax(use=r"use\b", as_=r"as\b"):
        token = stream.expect("use")
        path = parse_path(stream)

        alias = None
        if stream.get("as_"):
            alias = parse_identifier(stream)

        node = McdocUseStatement(path=path, alias=alias)
        return set_location(node, token, alias or path)


def parse_dispatch_statement(stream: TokenStream) -> McdocDispatchStatement:
    with stream.syntax(
        dispatch=r"dispatch\b",
        bracket=r"\[|\]",
        angle=r"<|>",
        to=r"to\b",
    ):
        attributes = parse_attributes(stream)

        token = stream.expect("dispatch")

        resource_location = parse_resource_location(stream)

        open_bracket = stream.expect(("bracket", "["))
        indices: List[McdocStaticIndex] = []
        close_bracket = expect_sequence(
            stream,
            indices,
            parse_static_index,
            until=("bracket", "]"),
        )

        if not indices:
            exc = InvalidSyntax("Expected at least one index.")
            raise set_location(exc, open_bracket, close_bracket)

        parameters: List[McdocIdentifier] = []
        if stream.get(("angle", "<")):
            expect_sequence(
                stream,
                parameters,
                parse_identifier,
                until=("angle", ">"),
            )

        stream.expect("to")

        type = parse_type(stream)

        node = McdocDispatchStatement(
            attributes=attributes,
            resource_location=resource_location,
            indices=McdocChildren(indices),
            parameters=McdocChildren(parameters),
            type=type,
        )
        return set_location(node, attributes[0] if attributes else token, type)


def parse_attributes(stream: TokenStream) -> McdocChildren[McdocAttribute]:
    with stream.syntax(attribute=r"#\[|\]", equal=r"="):
        attributes: List[McdocAttribute] = []

        for open_attribute in stream.collect(("attribute", "#[")):
            identifier = parse_identifier(stream)

            if close_attribute := stream.get(("attribute", "]")):
                value = None
            else:
                if stream.get("equal"):
                    value = choose_alternative(stream, parse_type, parse_attribute_tree)
                else:
                    value = parse_attribute_tree(stream)
                close_attribute = stream.expect(("attribute", "]"))

            node = McdocAttribute(identifier=identifier, value=value)
            attributes.append(set_location(node, open_attribute, close_attribute))

        return McdocChildren(attributes)


def parse_attribute_tree(stream: TokenStream) -> McdocAttributeTree:
    with stream.syntax(brace=r"\(|\)", bracket=r"\[|\]", curly=r"\{|\}", comma=r","):
        open_tree = stream.expect_any(
            ("brace", "("),
            ("bracket", "["),
            ("curly", "{"),
        )

        close_pattern = (
            ("brace", ")")
            if open_tree.match("brace")
            else ("bracket", "]")
            if open_tree.match("bracket")
            else ("curly", "}")
        )

        positional_values: List[McdocAttributeValue] = []
        named_values: List[McdocAttributeTreeNamedValue] = []

        for _ in stream.peek_until(close_pattern):
            value = choose_alternative(
                stream,
                parse_attribute_tree,
                parse_attribute_tree_named_value,
                parse_type,
            )

            if isinstance(value, McdocAttributeTreeNamedValue):
                named_values.append(value)
            elif not named_values:
                positional_values.append(value)
            else:
                exc = InvalidSyntax("Invalid positional value after named value.")
                raise set_location(exc, value)

            if not stream.get("comma"):
                stream.expect(close_pattern)
                break

        node = McdocAttributeTree(
            flavor=close_pattern[0],
            positional_values=McdocChildren(positional_values),
            named_values=McdocChildren(named_values),
        )
        return set_location(node, open_tree, stream.current)


def parse_attribute_tree_named_value(
    stream: TokenStream,
) -> McdocAttributeTreeNamedValue:
    with stream.syntax(equal=r"="):
        name = choose_alternative(stream, parse_string, parse_identifier)

        if stream.get("equal"):
            value = choose_alternative(stream, parse_type, parse_attribute_tree)
        else:
            value = parse_attribute_tree(stream)

        node = McdocAttributeTreeNamedValue(name=name, value=value)
        return set_location(node, name, value)


def expect_sequence(
    stream: TokenStream,
    nodes: List[McdocNodeType],
    parser: Callable[[TokenStream], McdocNodeType],
    until: TokenPattern,
    separator: str = r",",
):
    with stream.syntax(separator=separator):
        for _ in stream.peek_until(until):
            nodes.append(parser(stream))
            if not stream.get("separator"):
                stream.expect(until)
                break
        return stream.current


def choose_alternative(
    stream: TokenStream,
    *args: Callable[[TokenStream], McdocNodeType],
) -> McdocNodeType:
    for parser, alternative in stream.choose(*args):
        with alternative:
            return parser(stream)
    raise ValueError("Unreachable!")
