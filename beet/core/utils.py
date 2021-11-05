__all__ = [
    "JsonDict",
    "FileSystemPath",
    "Sentinel",
    "SENTINEL_OBJ",
    "dump_json",
    "extra_field",
    "required_field",
    "intersperse",
    "normalize_string",
    "snake_case",
    "log_time",
]


import json
import logging
import re
import time
from contextlib import contextmanager
from dataclasses import field
from pathlib import PurePath
from typing import Any, Dict, Iterable, Iterator, List, TypeVar, Union

T = TypeVar("T")


JsonDict = Dict[str, Any]
FileSystemPath = Union[str, PurePath]
TextComponent = Union[str, List[Any], JsonDict]


class Sentinel:
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


SENTINEL_OBJ = Sentinel()


def dump_json(value: Any) -> str:
    return json.dumps(value, indent=2) + "\n"


def extra_field(**kwargs: Any) -> Any:
    return field(repr=False, hash=False, compare=False, **kwargs)


def required_field(**kwargs: Any) -> Any:
    return field(**kwargs, default_factory=_raise_required_field)


def _raise_required_field():
    raise ValueError("Field required.")


def intersperse(iterable: Iterable[T], delimitter: T) -> Iterator[T]:
    it = iter(iterable)
    yield next(it)
    for x in it:
        yield delimitter
        yield x


NORMALIZE_REGEX = re.compile(r"[^a-z0-9]+")


def normalize_string(string: str) -> str:
    return NORMALIZE_REGEX.sub("_", string.lower()).strip("_")


CAMEL_REGEX = re.compile(r"((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))")


def snake_case(string: str) -> str:
    return CAMEL_REGEX.sub(r"_\1", string).lower()


time_logger = logging.getLogger("time")


@contextmanager
def log_time(message: str, *args: Any, **kwargs: Any) -> Iterator[None]:
    start = time.time()
    try:
        yield
    finally:
        message = f"{message} (took {time.time() - start:.2f}s)"
        time_logger.debug(message, *args, **kwargs)
