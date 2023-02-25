__all__ = [
    "K",
    "CK",
    "V",
    "CV",
    "PinDefault",
    "PinDefaultFactory",
    "SupportsKeys",
    "Drop",
    "SupportsMerge",
    "MergeableType",
    "MergeMixin",
    "MatchMixin",
    "Pin",
    "Container",
    "MergeContainer",
    "ContainerProxy",
]


import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    Generic,
    Iterable,
    Iterator,
    KeysView,
    Mapping,
    MutableMapping,
    Optional,
    Protocol,
    TypeGuard,
    TypeVar,
    get_args,
    get_origin,
    overload,
)

from pathspec import PathSpec
from typing_extensions import Self

from .utils import SENTINEL_OBJ, Sentinel

K = TypeVar("K")
CK = TypeVar("CK", covariant=True)
V = TypeVar("V")
CV = TypeVar("CV", covariant=True)
ProxyKeyType = TypeVar("ProxyKeyType")

PinDefault = V | Sentinel
PinDefaultFactory = Callable[[], V] | Sentinel


class SupportsKeys(Generic[CK], Protocol):
    def keys(self) -> KeysView[CK]:
        ...


class Drop(Exception):
    """Raised to signal that an item shouldn't be added to a container."""


class SupportsMerge(Protocol):
    """Protocol for detecting mergeable types."""

    def merge(self, other: Self) -> bool:
        ...


MergeableType = TypeVar("MergeableType", bound=SupportsMerge)


class MergeMixin(MutableMapping[K, MergeableType]):
    def merge(self, other: Mapping[K, MergeableType]) -> bool:
        """Merge values from the given dict-like object."""
        for key, value in other.items():
            try:
                if key not in self or not self[key].merge(value):
                    self[key] = value
            except Drop:
                del self[key]
        return True


class MatchMixin:
    def match(self: SupportsKeys[str], *patterns: str) -> set[str]:
        """Return keys matching the given path patterns."""
        spec = PathSpec.from_lines("gitwildmatch", patterns)
        return {
            key
            for key in self.keys()
            if spec.match_file(key)  # pyright: ignore[reportUnknownMemberType]
        }


logger = logging.getLogger(__name__)


@dataclass
class Pin(Generic[K, CV]):
    """Descriptor that exposes a specific value from a dict-like object."""

    key: K
    default: PinDefault[CV] = SENTINEL_OBJ
    default_factory: PinDefaultFactory[CV] = SENTINEL_OBJ

    def __post_init__(self):
        if not isinstance(self.default, Sentinel) and not isinstance(
            self.default_factory, Sentinel
        ):
            logger.warning(
                "Both default and default_factory were set, default will be ignored and only the default_factory will be used"
            )

    @overload
    def __get__(self, obj: None, objtype: None) -> Self:
        ...

    @overload
    def __get__(self, obj: Any, objtype: type[Any]) -> CV:
        ...

    def __get__(
        self, obj: Optional[Any], objtype: Optional[type[Any]] = None
    ) -> CV | Self:
        if obj is None:
            return self

        mapping = self.forward(obj)

        while True:
            try:
                return mapping[self.key]
            except KeyError:
                value = (
                    self.default
                    if isinstance(self.default_factory, Sentinel)
                    else self.default_factory()
                )

                if isinstance(value, Sentinel):
                    raise

                mapping[self.key] = value

    def __set__(self: "Pin[K, V]", obj: Any, value: V):
        self.forward(obj)[self.key] = value

    def __delete__(self, obj: Any):
        del self.forward(obj)[self.key]

    def forward(self, obj: Any) -> Any:
        """Return the dict-like object that contains the pinned value."""
        return obj

    @classmethod
    def collect_from(cls, target: type[Any]) -> dict[str, "Pin[K, CV]"]:
        return {
            key: value for key, value in vars(target).items() if isinstance(value, cls)
        }


class Container(MutableMapping[K, V]):
    """Generic dict-like container."""

    _wrapped: dict[K, V]

    def __init__(self):
        self._wrapped = {}

    def __getitem__(self, key: K) -> V:
        key = self.normalize_key(key)

        try:
            return self._wrapped[key]
        except KeyError:
            pass

        value = self.missing(key)
        self[key] = value
        return value

    def __setitem__(self, key: K, value: V):
        key = self.normalize_key(key)

        should_delete = False

        try:
            value = self.process(key, value)
        except Drop:
            should_delete = True

        self._wrapped[key] = value

        if should_delete:
            del self[key]

    def __delitem__(self, key: K):
        key = self.normalize_key(key)
        del self._wrapped[key]

    def __iter__(self) -> Iterator[K]:
        return iter(self._wrapped)

    def __len__(self) -> int:
        return len(self._wrapped)

    def normalize_key(self, key: K) -> K:
        """Normalize the key before accessing an item."""
        return key

    def process(self, key: K, value: V) -> V:
        """Process the value before inserting it."""
        return value

    def missing(self, key: K) -> V:
        """Recover missing item or raise a KeyError."""
        raise KeyError(key)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(keys={list(self.keys())})"


class MergeContainer(MergeMixin[K, MergeableType], Container[K, MergeableType]):
    pass


class ContainerProxy(ABC, Generic[ProxyKeyType, K, V], MutableMapping[K, V]):
    """Generic aggregated view over several nested bounded dict-like objects."""

    proxy: Mapping[K, Mapping[ProxyKeyType, MutableMapping[K, V]]]
    proxy_key: ProxyKeyType

    def __init__(
        self,
        proxy: Mapping[K, Mapping[ProxyKeyType, MutableMapping[K, V]]],
        proxy_key: ProxyKeyType,
    ):
        self.proxy = proxy
        self.proxy_key = proxy_key

    def __getitem__(self, key: K) -> V:
        key1, key2 = self.split_key(key)
        return self.proxy[key1][self.proxy_key][key2]

    def __setitem__(self, key: K, value: V):
        key1, key2 = self.split_key(key)
        self.proxy[key1][self.proxy_key][key2] = value

    def __delitem__(self, key: K):
        key1, key2 = self.split_key(key)
        del self.proxy[key1][self.proxy_key][key2]

    def __iter__(self) -> Iterator[K]:
        for key1, mapping in self.proxy.items():
            for key2 in mapping[self.proxy_key]:
                yield self.join_key(key1, key2)

    def __len__(self) -> int:
        return sum(len(mapping[self.proxy_key]) for mapping in self.proxy.values())

    @abstractmethod
    def split_key(self, key: K) -> tuple[K, K]:
        """Return the outer mapping key and the nested key."""
        ...

    @abstractmethod
    def join_key(self, key1: K, key2: K) -> K:
        """Combine the outer mapping key and the nested key."""
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(keys={list(self.keys())})"


class MergeContainerProxy(
    MergeMixin[K, MergeableType],
    ContainerProxy[ProxyKeyType, K, MergeableType],
    Generic[ProxyKeyType, K, MergeableType],
):
    pass


# TODO: Use actual union of possible generic values
ResolvedGeneric = Any
ResolvedGenerics = Mapping[TypeVar, ResolvedGeneric]


BaseType = TypeVar("BaseType", bound=type[Any])


def is_subclass_type(cls: Any, base: BaseType) -> TypeGuard[BaseType]:
    # TODO: Check if it is necessary to get the origin of base
    return isinstance(cls := get_origin(cls) or cls, type) and issubclass(cls, base)


def get_orig_bases(cls: Any) -> Iterable[Any]:
    return getattr(cls, "__orig_bases__", [])


def resolve_base_generics(
    cls: BaseType | Any, base: BaseType, generics: ResolvedGenerics = {}
) -> Optional[ResolvedGenerics]:
    if not is_subclass_type(cls, base):
        return None

    # TODO: Support caching the generic tree on types that implement a protocol

    if (
        (args := get_args(cls))
        and (origin := get_origin(cls))
        and (params := getattr(origin, "__parameters__", None))
    ):
        next_generics: dict[TypeVar, ResolvedGeneric] = {}
        for param, arg in zip(params, args, strict=True):
            # TODO: Support keeping the full sequence of TypeVars between the desired TypeVar and the original class
            if isinstance(arg, TypeVar) and (value := generics.get(arg)):
                next_generics[param] = value
            else:
                next_generics[param] = arg

        # TODO: Check if it is necessary to call get_origin on base
        if origin == base:
            return next_generics

        for orig_base in get_orig_bases(origin):
            if (
                res := resolve_base_generics(orig_base, base, next_generics)
            ) is not None:
                return res
    else:
        for orig_base in get_orig_bases(cls):
            if (res := resolve_base_generics(orig_base, base)) is not None:
                return res

    return None
