__all__ = [
    "LoopInfo",
    "loop_info",
]


from dataclasses import dataclass, field
from typing import (
    Any,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
    overload,
)

from beet.core.utils import SENTINEL_OBJ, Sentinel

T = TypeVar("T")
U = TypeVar("U")


def loop_info(iterable: Iterable[T]) -> "LoopInfo[T]":
    return LoopInfo(iterable, iter(iterable))


@dataclass
class LoopInfo(Generic[T]):
    iterable: Iterable[T]
    iterator: Iterator[T]

    index: int = -1
    accumulator: List[T] = field(default_factory=list)

    def __iter__(self) -> "LoopInfo[T]":
        return self

    def __next__(self) -> Tuple["LoopInfo[T]", T]:
        while self.index + 1 >= len(self.accumulator):
            self.accumulator.append(next(self.iterator))
        self.index += 1
        return self, self.current

    @overload
    def peek(self, offset: int) -> Optional[T]:
        ...

    @overload
    def peek(self, offset: int, default: U) -> Union[T, U]:
        ...

    def peek(self, offset: int, default: Any = None) -> Any:
        index = self.index + offset

        if index < 0:
            return default

        try:
            while index >= len(self.accumulator):
                self.accumulator.append(next(self.iterator))
        except StopIteration:
            return default

        return self.accumulator[index]

    @property
    def before(self) -> Optional[T]:
        return self.peek(-1)

    @property
    def current(self) -> T:
        return self.accumulator[self.index]

    @property
    def after(self) -> Optional[T]:
        return self.peek(1)

    @property
    def count(self) -> int:
        try:
            return len(self.iterable)  # type: ignore
        except TypeError:
            self.accumulator.extend(self.iterator)
            return len(self.accumulator)

    @property
    def first(self) -> bool:
        return self.index == 0

    @property
    def last(self) -> bool:
        return isinstance(self.peek(1, SENTINEL_OBJ), Sentinel)

    def cycle(self, arg: U, *args: U) -> U:
        args = (arg,) + args
        return args[self.index % len(args)]
