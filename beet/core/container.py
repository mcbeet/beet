__all__ = [
    "MatchMixin",
    "SupportsMerge",
    "MergeMixin",
    "Container",
    "ContainerProxy",
]


from dataclasses import dataclass, field
from typing import (
    Dict,
    Generic,
    Iterator,
    Mapping,
    MutableMapping,
    Protocol,
    Set,
    Tuple,
    TypeVar,
)

from pathspec import PathSpec


class MatchMixin:
    def match(self: Mapping[str, object], *patterns: str) -> Set[str]:
        """Return keys matching the given path patterns."""
        spec = PathSpec.from_lines("gitwildmatch", patterns or ["*"])
        return set(spec.match_files(self.keys()))


K = TypeVar("K")
V = TypeVar("V")


class SupportsMerge(Protocol[V]):
    """Protocol for detecting mergeable types."""

    def merge(self: V, other: V) -> bool:
        ...


MergeableType = TypeVar("MergeableType", bound="SupportsMerge[object]")


class MergeMixin:
    def merge(
        self: MutableMapping[K, MergeableType],
        other: Mapping[K, MergeableType],
    ) -> bool:
        """Merge values from the given dict-like object."""
        for key, value in other.items():
            if current := self.get(key):
                if current.merge(value):
                    continue
            self[key] = value
        return True


@dataclass
class Container(MutableMapping[K, V]):
    """Generic dict-like container.

    The class wraps a builtin dictionnary and exposes overrideable hooks
    for intercepting updates and missing items.
    """

    _wrapped: Dict[K, V] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self):
        for key, value in self._wrapped.items():
            self.process(key, value)

    def __getitem__(self, key: K) -> V:
        try:
            return self._wrapped[key]
        except KeyError:
            pass

        value = self.missing(key)
        self[key] = value
        return value

    def __setitem__(self, key: K, value: V):
        self._wrapped[key] = self.process(key, value)

    def __delitem__(self, key: K):
        del self._wrapped[key]

    def __iter__(self) -> Iterator[K]:
        return iter(self._wrapped)

    def __len__(self) -> int:
        return len(self._wrapped)

    def process(self, key: K, value: V) -> V:
        """Process the value before inserting it."""
        return value

    def missing(self, key: K) -> V:
        """Recover missing item or raise a KeyError."""
        raise KeyError(key)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(keys={list(self.keys())})"


ProxyKeyType = TypeVar("ProxyKeyType")


@dataclass
class ContainerProxy(Generic[ProxyKeyType, K, V], MutableMapping[K, V]):
    """Generic aggregated view over several nested bounded dict-like objects."""

    proxy: Mapping[K, Mapping[ProxyKeyType, MutableMapping[K, V]]]
    proxy_key: ProxyKeyType

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
