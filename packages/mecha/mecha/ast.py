__all__ = [
    "AstNode",
    "AstChildren",
    "AstRoot",
    "AstCommand",
    "AstLiteral",
    "AstString",
    "AstBool",
    "AstNumber",
    "AstUUID",
    "AstCoordinate",
    "AstVector2",
    "AstVector3",
    "AstJson",
    "AstJsonValue",
    "AstJsonArray",
    "AstJsonObjectKey",
    "AstJsonObjectEntry",
    "AstJsonObject",
    "AstNbt",
    "AstNbtValue",
    "AstNbtList",
    "AstNbtCompoundKey",
    "AstNbtCompoundEntry",
    "AstNbtCompound",
    "AstNbtByteArray",
    "AstNbtIntArray",
    "AstNbtLongArray",
    "AstResourceLocation",
    "AstBlockState",
    "AstBlock",
    "AstItem",
    "AstRange",
    "AstTime",
    "AstSelectorScoreMatch",
    "AstSelectorScores",
    "AstSelectorAdvancementPredicateMatch",
    "AstSelectorAdvancementMatch",
    "AstSelectorArgument",
    "AstSelector",
    "AstMessage",
    "AstNbtPathSubscript",
    "AstNbtPath",
    "AstParticleParameters",
    "AstDustParticleParameters",
    "AstDustColorTransitionParticleParameters",
    "AstBlockParticleParameters",
    "AstFallingDustParticleParameters",
    "AstItemParticleParameters",
    "AstVibrationParticleParameters",
    "AstParticle",
]


from dataclasses import dataclass, fields
from typing import (
    Any,
    ClassVar,
    Iterator,
    Literal,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
)
from uuid import UUID

from beet.core.utils import extra_field, required_field

# pyright: reportMissingTypeStubs=false
from nbtlib import ByteArray, Compound, IntArray
from nbtlib import List as ListTag
from nbtlib import LongArray
from tokenstream import UNKNOWN_LOCATION, SourceLocation, set_location

T = TypeVar("T")
AstNodeType = TypeVar("AstNodeType", bound="AstNode")


@dataclass(frozen=True)
class AstNode:
    """Base class for all ast nodes."""

    location: SourceLocation = extra_field(default=UNKNOWN_LOCATION)
    end_location: SourceLocation = extra_field(default=UNKNOWN_LOCATION)

    parser: ClassVar[Optional[str]] = None

    def __iter__(self) -> Iterator["AstNode"]:
        for f in fields(self):
            attribute = getattr(self, f.name)

            if isinstance(attribute, AstChildren):
                yield from attribute

            if isinstance(attribute, AstNode):
                yield attribute

    def walk(self) -> Iterator["AstNode"]:
        yield self

        for f in fields(self):
            attribute = getattr(self, f.name)

            if isinstance(attribute, AstChildren):
                for child in attribute:  # type: ignore
                    if isinstance(child, AstNode):
                        yield from child.walk()

            elif isinstance(attribute, AstNode):
                yield from attribute.walk()

    def dump(self, prefix: str = "") -> str:
        """Return a pretty-printed representation of the ast."""
        return f"{prefix}{self.__class__}\n" + "\n".join(
            f"{prefix}  {f.name}:"
            + (
                "\n" + ("\n".join(child.dump(prefix + "    ") for child in attribute) if attribute else prefix + "    <empty>")  # type: ignore
                if isinstance(attribute := getattr(self, f.name), AstChildren)
                else "\n" + attribute.dump(prefix + "    ")
                if isinstance(attribute, AstNode)
                else f" {attribute!r}"
            )
            for f in fields(self)
        )

    def emit_error(self, exc: T) -> T:
        """Add location information to invalid syntax exceptions."""
        return set_location(exc, self)


class AstChildren(Tuple[AstNodeType, ...]):
    """Specialized tuple subclass for holding multiple child ast nodes."""


@dataclass(frozen=True)
class AstRoot(AstNode):
    """Root ast node"""

    commands: AstChildren["AstCommand"] = required_field()

    parser = "root"


@dataclass(frozen=True)
class AstCommand(AstNode):
    """Command ast node"""

    identifier: str = required_field()
    arguments: AstChildren[AstNode] = required_field()

    parser = "command"


@dataclass(frozen=True)
class AstLiteral(AstNode):
    """Ast literal node."""

    value: str = required_field()

    parser = "literal"


@dataclass(frozen=True)
class AstString(AstNode):
    """Ast string node."""

    value: str = required_field()

    parser = "phrase"


@dataclass(frozen=True)
class AstBool(AstNode):
    """Ast bool node."""

    value: bool = required_field()

    parser = "bool"


@dataclass(frozen=True)
class AstNumber(AstNode):
    """Ast number node."""

    value: Union[int, float] = required_field()

    parser = "numeric"


@dataclass(frozen=True)
class AstUUID(AstNode):
    """Ast uuid node."""

    value: UUID = required_field()

    parser = "uuid"


@dataclass(frozen=True)
class AstCoordinate(AstNode):
    """Coordinate ast node."""

    type: Literal["absolute", "relative", "local"] = "absolute"
    value: Union[int, float] = required_field()

    parser = "coordinate"


@dataclass(frozen=True)
class AstVector2(AstNode):
    """Vector 2 ast node."""

    x: AstCoordinate = required_field()
    y: AstCoordinate = required_field()


@dataclass(frozen=True)
class AstVector3(AstNode):
    """Vector 3 ast node."""

    x: AstCoordinate = required_field()
    y: AstCoordinate = required_field()
    z: AstCoordinate = required_field()


@dataclass(frozen=True)
class AstJson(AstNode):
    """Base ast node for json."""

    parser = "json"

    def evaluate(self) -> Any:
        """Return the json value."""
        raise NotImplementedError()

    @classmethod
    def from_value(cls, value: Any) -> "AstJson":
        """Create json ast nodes representing the specified json value."""
        if value is None or isinstance(value, (bool, str, int, float)):
            return AstJsonValue(value=value)
        elif isinstance(value, Mapping):
            object: Mapping[str, Any] = value
            return AstJsonObject(
                entries=AstChildren(
                    AstJsonObjectEntry(
                        key=AstJsonObjectKey(value=k),
                        value=cls.from_value(v),
                    )
                    for k, v in object.items()
                )
            )
        elif isinstance(value, Sequence):
            array: Sequence[Any] = value
            return AstJsonArray(elements=AstChildren(cls.from_value(e) for e in array))
        else:
            raise ValueError(f"Invalid json value of type {type(value)!r}.")


@dataclass(frozen=True)
class AstJsonValue(AstJson):
    """Ast json value node."""

    value: Any = required_field()

    parser = None

    def evaluate(self) -> Any:
        return self.value


@dataclass(frozen=True)
class AstJsonArray(AstJson):
    """Ast json array node."""

    elements: AstChildren[AstJson] = required_field()

    parser = None

    def evaluate(self) -> Any:
        return [element.evaluate() for element in self.elements]


@dataclass(frozen=True)
class AstJsonObjectKey(AstNode):
    """Ast json object key node."""

    value: str = required_field()


@dataclass(frozen=True)
class AstJsonObjectEntry(AstNode):
    """Ast json object entry node."""

    key: AstJsonObjectKey = required_field()
    value: AstJson = required_field()


@dataclass(frozen=True)
class AstJsonObject(AstJson):
    """Ast json object node."""

    entries: AstChildren[AstJsonObjectEntry] = required_field()

    parser = "json"

    def evaluate(self) -> Any:
        return {entry.key.value: entry.value.evaluate() for entry in self.entries}


@dataclass(frozen=True)
class AstNbt(AstNode):
    """Base ast node for nbt."""

    parser = "nbt"

    def evaluate(self) -> Any:
        """Return the nbt value."""
        raise NotImplementedError()


@dataclass(frozen=True)
class AstNbtValue(AstNbt):
    """Ast nbt value node."""

    value: Any = required_field()

    parser = None

    def evaluate(self) -> Any:
        return self.value


@dataclass(frozen=True)
class AstNbtList(AstNbt):
    """Ast nbt list node."""

    elements: AstChildren[AstNbt] = required_field()

    parser = None

    def evaluate(self) -> Any:
        return ListTag([element.evaluate() for element in self.elements])  # type: ignore


@dataclass(frozen=True)
class AstNbtCompoundKey(AstNode):
    """Ast nbt compound key node."""

    value: str = required_field()


@dataclass(frozen=True)
class AstNbtCompoundEntry(AstNode):
    """Ast nbt compound entry node."""

    key: AstNbtCompoundKey = required_field()
    value: AstNbt = required_field()


@dataclass(frozen=True)
class AstNbtCompound(AstNbt):
    """Ast nbt compound node."""

    entries: AstChildren[AstNbtCompoundEntry] = required_field()

    parser = "nbt_compound"

    def evaluate(self) -> Any:
        return Compound(  # type: ignore
            {entry.key.value: entry.value.evaluate() for entry in self.entries},
        )


@dataclass(frozen=True)
class AstNbtByteArray(AstNbt):
    """Ast nbt byte array node."""

    elements: AstChildren[AstNbt] = required_field()

    parser = None

    def evaluate(self) -> Any:
        return ByteArray([element.evaluate() for element in self.elements])  # type: ignore


@dataclass(frozen=True)
class AstNbtIntArray(AstNbt):
    """Ast nbt int array node."""

    elements: AstChildren[AstNbt] = required_field()

    parser = None

    def evaluate(self) -> Any:
        return IntArray([element.evaluate() for element in self.elements])  # type: ignore


@dataclass(frozen=True)
class AstNbtLongArray(AstNbt):
    """Ast nbt long array node."""

    elements: AstChildren[AstNbt] = required_field()

    parser = None

    def evaluate(self) -> Any:
        return LongArray([element.evaluate() for element in self.elements])  # type: ignore


@dataclass(frozen=True)
class AstResourceLocation(AstNode):
    """Ast resource location node."""

    is_tag: bool = False
    namespace: Optional[str] = None
    path: str = required_field()

    parser = "resource_location_or_tag"

    @classmethod
    def from_value(cls, value: str) -> "AstResourceLocation":
        """Create a resource location node representing the given value."""
        if is_tag := value.startswith("#"):
            value = value[1:]
        namespace, _, path = value.rpartition(":")
        return cls(is_tag=is_tag, namespace=namespace or None, path=path)

    def get_value(self) -> str:
        """Return the value of the resource location as a string."""
        prefix = "#" if self.is_tag else ""
        namespace = f"{self.namespace}:" if self.namespace else ""
        return prefix + namespace + self.path

    def get_canonical_value(self) -> str:
        """Return the canonical value of the resource location as a string."""
        prefix = "#" if self.is_tag else ""
        namespace = f"{self.namespace}:" if self.namespace else "minecraft:"
        return prefix + namespace + self.path


@dataclass(frozen=True)
class AstBlockState(AstNode):
    """Ast block state node."""

    key: AstString = required_field()
    value: AstString = required_field()


@dataclass(frozen=True)
class AstBlock(AstNode):
    """Ast block node."""

    identifier: AstResourceLocation = required_field()
    block_states: AstChildren[AstBlockState] = AstChildren()
    data_tags: Optional[AstNbt] = None


@dataclass(frozen=True)
class AstItem(AstNode):
    """Ast item node."""

    identifier: AstResourceLocation = required_field()
    data_tags: Optional[AstNbt] = None


@dataclass(frozen=True)
class AstRange(AstNode):
    """Ast range node."""

    min: Optional[Union[int, float]] = required_field()
    max: Optional[Union[int, float]] = required_field()

    @property
    def exact(self) -> bool:
        """Wether the range is an exact match."""
        return self.min == self.max

    @property
    def value(self) -> Union[int, float]:
        """Return the exact value."""
        return self.min  # type: ignore

    parser = "range"


@dataclass(frozen=True)
class AstTime(AstNode):
    """Ast time node."""

    value: Union[int, float] = required_field()
    unit: Literal["day", "second", "tick"] = "tick"

    parser = "time"


@dataclass(frozen=True)
class AstSelectorScoreMatch(AstNode):
    """Ast selector score match node."""

    key: AstLiteral = required_field()
    value: AstRange = required_field()


@dataclass(frozen=True)
class AstSelectorScores(AstNode):
    """Ast selector scores node."""

    scores: AstChildren[AstSelectorScoreMatch] = required_field()


@dataclass(frozen=True)
class AstSelectorAdvancementPredicateMatch(AstNode):
    """Ast selector advancement predicate match node."""

    key: AstLiteral = required_field()
    value: AstBool = required_field()


@dataclass(frozen=True)
class AstSelectorAdvancementMatch(AstNode):
    """Ast selector advancement match node."""

    key: AstResourceLocation = required_field()
    value: Union[
        AstBool, AstChildren[AstSelectorAdvancementPredicateMatch]
    ] = required_field()


@dataclass(frozen=True)
class AstSelectorAdvancements(AstNode):
    """Ast selector advancements node."""

    advancements: AstChildren[AstSelectorAdvancementMatch] = required_field()


@dataclass(frozen=True)
class AstSelectorArgument(AstNode):
    """Ast selector argument node."""

    inverted: bool = False
    key: AstString = required_field()
    value: Optional[AstNode] = required_field()


@dataclass(frozen=True)
class AstSelector(AstNode):
    """Ast selector node."""

    variable: Literal["p", "r", "a", "e", "s"] = required_field()
    arguments: AstChildren[AstSelectorArgument] = AstChildren()

    parser = "selector"


@dataclass(frozen=True)
class AstMessage(AstNode):
    """Ast message node."""

    fragments: AstChildren[Union[AstLiteral, AstSelector]] = required_field()


@dataclass(frozen=True)
class AstNbtPathSubscript(AstNode):
    """Ast nbt path subscript node."""

    index: Union[None, AstNumber, AstNbtCompound] = None


@dataclass(frozen=True)
class AstNbtPath(AstNode):
    """Ast nbt path node."""

    components: AstChildren[
        Union[AstString, AstNbtCompound, AstNbtPathSubscript]
    ] = required_field()

    parser = "nbt_path"


@dataclass(frozen=True)
class AstParticleParameters(AstNode):
    """Base ast node for particle parameters."""


@dataclass(frozen=True)
class AstDustParticleParameters(AstParticleParameters):
    """Ast dust particle parameters node."""

    red: AstNumber = required_field()
    green: AstNumber = required_field()
    blue: AstNumber = required_field()
    size: AstNumber = required_field()


@dataclass(frozen=True)
class AstDustColorTransitionParticleParameters(AstParticleParameters):
    """Ast dust color transition particle parameters node."""

    red: AstNumber = required_field()
    green: AstNumber = required_field()
    blue: AstNumber = required_field()
    size: AstNumber = required_field()
    end_red: AstNumber = required_field()
    end_green: AstNumber = required_field()
    end_blue: AstNumber = required_field()


@dataclass(frozen=True)
class AstBlockParticleParameters(AstParticleParameters):
    """Ast block particle parameters node."""

    block: AstBlock = required_field()


@dataclass(frozen=True)
class AstFallingDustParticleParameters(AstParticleParameters):
    """Ast falling dust particle parameters node."""

    block: AstBlock = required_field()


@dataclass(frozen=True)
class AstItemParticleParameters(AstParticleParameters):
    """Ast item particle parameters node."""

    item: AstItem = required_field()


@dataclass(frozen=True)
class AstVibrationParticleParameters(AstParticleParameters):
    """Ast vibration particle parameters node."""

    x1: AstNumber = required_field()
    y1: AstNumber = required_field()
    z1: AstNumber = required_field()
    x2: AstNumber = required_field()
    y2: AstNumber = required_field()
    z2: AstNumber = required_field()
    duration: AstNumber = required_field()


@dataclass(frozen=True)
class AstParticle(AstNode):
    """Ast particle node."""

    name: AstResourceLocation = required_field()
    parameters: Optional[AstParticleParameters] = None

    parser = "particle"
