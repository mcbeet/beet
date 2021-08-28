__all__ = [
    "AstNode",
    "AstChildren",
    "AstRoot",
    "AstCommand",
    "AstValue",
    "AstCoordinate",
    "AstVector2",
    "AstVector3",
    "AstJson",
    "AstJsonValue",
    "AstJsonArray",
    "AstJsonObjectEntry",
    "AstJsonObject",
]


from dataclasses import dataclass, field, fields
from typing import (
    Any,
    Generic,
    Iterator,
    List,
    Literal,
    Optional,
    Tuple,
    TypeVar,
    Union,
)

from beet.core.utils import JsonDict
from tokenstream import SourceLocation

T = TypeVar("T")
NumericType = TypeVar("NumericType", float, int)
AstNodeType = TypeVar("AstNodeType", bound="AstNode")


@dataclass(frozen=True)
class AstNode:
    """Base class for all ast nodes."""

    location: SourceLocation = field(repr=False, hash=False, compare=False)
    end_location: SourceLocation = field(repr=False, hash=False, compare=False)

    def __iter__(self) -> Iterator["AstNode"]:
        yield self

        for f in fields(self):
            attribute = getattr(self, f.name)

            if isinstance(attribute, AstChildren):
                for child in attribute:  # type: ignore
                    yield from child

            elif isinstance(attribute, AstNode):
                yield from attribute

    def dump(self, prefix: str = "") -> str:
        """Return a pretty-printed representation of the ast."""
        return f"{prefix}{self.__class__}\n" + "\n".join(
            f"{prefix}  {f.name}:"
            + (
                "\n" + "\n".join(child.dump(prefix + "    ") for child in attribute)  # type: ignore
                if isinstance(attribute := getattr(self, f.name), AstChildren)
                else "\n" + attribute.dump(prefix + "    ")
                if isinstance(attribute, AstNode)
                else f" {attribute!r}"
            )
            for f in fields(self)
        )


class AstChildren(Tuple[AstNodeType, ...]):
    """Specialized tuple subclass for holding multiple child ast nodes."""


@dataclass(frozen=True)
class AstRoot(AstNode):
    """Root ast node"""

    filename: Optional[str]
    commands: AstChildren["AstCommand"]


@dataclass(frozen=True)
class AstCommand(AstNode):
    """Command ast node"""

    identifier: str
    arguments: AstChildren[AstNode]


@dataclass(frozen=True)
class AstValue(AstNode, Generic[T]):
    """Value ast node"""

    value: T


@dataclass(frozen=True)
class AstCoordinate(AstValue[NumericType]):
    """Coordinate ast node."""

    prefix: Literal["absolute", "relative", "local"]


@dataclass(frozen=True)
class AstVector2(AstNode, Generic[NumericType]):
    """Vector 2 ast node."""

    x: AstCoordinate[NumericType]
    y: AstCoordinate[NumericType]


@dataclass(frozen=True)
class AstVector3(AstNode, Generic[NumericType]):
    """Vector 3 ast node."""

    x: AstCoordinate[NumericType]
    y: AstCoordinate[NumericType]
    z: AstCoordinate[NumericType]


@dataclass(frozen=True)
class AstJson(AstNode):
    """Base ast node for json."""

    def get_value(self) -> Any:
        """Return the json value."""
        raise NotImplementedError()


@dataclass(frozen=True)
class AstJsonValue(AstJson):
    """Ast json value node."""

    value: Union[None, bool, str, float]

    def get_value(self) -> Union[None, bool, str, float]:
        return self.value


@dataclass(frozen=True)
class AstJsonArray(AstJson):
    """Ast json array node."""

    elements: AstChildren[AstJson]

    def get_value(self) -> List[Any]:
        return [element.get_value() for element in self.elements]


@dataclass(frozen=True)
class AstJsonObjectEntry(AstNode):
    """Ast json object entry node."""

    key: AstValue[str]
    value: AstJson


@dataclass(frozen=True)
class AstJsonObject(AstJson):
    """Ast json object node."""

    entries: AstChildren[AstJsonObjectEntry]

    def get_value(self) -> JsonDict:
        return {entry.key.value: entry.value.get_value() for entry in self.entries}
