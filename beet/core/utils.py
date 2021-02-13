__all__ = [
    "JsonDict",
    "FileSystemPath",
    "Sentinel",
    "SENTINEL_OBJ",
    "dump_json",
    "extra_field",
    "intersperse",
]


import json
import os
from dataclasses import field
from typing import Any, Dict, Iterable, Iterator, List, TypeVar, Union

T = TypeVar("T")

JsonDict = Dict[str, Any]
FileSystemPath = Union[str, "os.PathLike[str]"]
TextComponent = Union[str, List[Any], JsonDict]


class Sentinel:
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


SENTINEL_OBJ = Sentinel()


def dump_json(value: Any) -> str:
    return json.dumps(value, indent=2) + "\n"


def extra_field(**kwargs: Any) -> Any:
    return field(repr=False, hash=False, compare=False, **kwargs)


def intersperse(iterable: Iterable[T], delimitter: T) -> Iterator[T]:
    it = iter(iterable)
    yield next(it)
    for x in it:
        yield delimitter
        yield x
