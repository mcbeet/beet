__all__ = [
    "SupportsMerge",
    "MergeMixin",
    "MatchMixin",
    "Pin",
    "PinDefault",
    "PinDefaultFactory",
    "Container",
    "ContainerProxy",
    "Drop",
]


from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterator,
    Mapping,
    MutableMapping,
    Optional,
    Protocol,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from pathspec import PathSpec

from .utils import SENTINEL_OBJ, Sentinel

K = TypeVar("K")
V = TypeVar("V")
CV = TypeVar("CV", covariant=True)
ProxyKeyType = TypeVar("ProxyKeyType")

PinDefault = Union[V, Sentinel]
PinDefaultFactory = Union[Callable[[], V], Sentinel]


class Drop(Exception):
    """Raised to signal that an item shouldn't be added to a container."""


class SupportsMerge(Protocol):
    """Protocol for detecting mergeable types."""

    def merge(self, other: Any) -> bool:
        ...


class MergeMixin:
    def merge(self, other: Mapping[Any, SupportsMerge]) -> bool:
        """Merge values from the given dict-like object."""
        if self is other:
            return True
        for key, value in other.items():
            try:
                if key not in self or not self[key].merge(value):  # type: ignore
                    self[key] = value  # type: ignore
            except Drop:
                del self[key]  # type: ignore
        return True


class MatchMixin:
    def match(self, *patterns: str) -> Set[str]:
        """Return keys matching the given path patterns."""
        spec = PathSpec.from_lines("gitwildmatch", patterns)
        return set(spec.match_files(self.keys()))  # type: ignore


@dataclass
class Pin(Generic[K, CV]):
    """Descriptor that exposes a specific value from a dict-like object."""

    key: K
    default: PinDefault[CV] = SENTINEL_OBJ
    default_factory: PinDefaultFactory[CV] = SENTINEL_OBJ

    def __get__(self, obj: Any, objtype: Optional[Type[Any]] = None) -> CV:
        mapping = self.forward(obj)

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
            return self.__get__(obj, objtype)

    def __set__(self: "Pin[K, V]", obj: Any, value: V):
        self.forward(obj)[self.key] = value

    def __delete__(self, obj: Any):
        del self.forward(obj)[self.key]

    def forward(self, obj: Any) -> Any:
        """Return the dict-like object that contains the pinned value."""
        return obj

    @classmethod
    def collect_from(
        cls: Type["Pin[K, CV]"], target: Type[Any]
    ) -> Dict[str, "Pin[K, CV]"]:
        return {
            key: value for key, value in vars(target).items() if isinstance(value, cls)
        }


class Container(MutableMapping[K, V]):
    """Generic dict-like container."""

    _wrapped: Dict[K, V]

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


class ContainerProxy(Generic[ProxyKeyType, K, V], MutableMapping[K, V]):
    """Generic aggregated view over several nested bounded dict-like objects."""

    proxy: Mapping[K, Mapping[ProxyKeyType, MutableMapping[K, V]]]
    proxy_key: ProxyKeyType

    def __init__(
        self,
        proxy: Mapping[K, Mapping[ProxyKeyType, MutableMapping[K, V]]],
        proxy_key: ProxyKeyType,
    ) -> None:
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

    def split_key(self, key: K) -> Tuple[K, K]:
        """Return the outer mapping key and the nested key."""
        raise NotImplementedError()

    def join_key(self, key1: K, key2: K) -> K:
        """Combine the outer mapping key and the nested key."""
        raise NotImplementedError()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(keys={list(self.keys())})"
