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
    "get_import_string",
    "import_from_string",
    "log_time",
    "remove_path",
]


import json
import logging
import re
import shutil
import time
from contextlib import contextmanager
from dataclasses import field
from importlib import import_module
from pathlib import Path, PurePath
from typing import Any, Dict, Iterable, Iterator, List, Optional, TypeVar, Union

from pydantic import PydanticTypeError
from pydantic.validators import _VALIDATORS  # type: ignore

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


def get_import_string(obj: Any) -> str:
    return f"{obj.__module__}.{obj.__qualname__}"


def import_from_string(
    dotted_path: str,
    default_member: Optional[str] = None,
    whitelist: Optional[List[str]] = None,
) -> Any:
    if whitelist is not None and dotted_path not in whitelist:
        raise ModuleNotFoundError(f"No module named {dotted_path!r}")
    try:
        module = import_module(dotted_path)
    except ImportError:
        if "." not in dotted_path:
            raise

        dotted_path, _, default_member = dotted_path.rpartition(".")

        try:
            module = import_module(dotted_path)
        except Exception as exc:
            raise exc from None

    return getattr(module, default_member) if default_member else module


time_logger = logging.getLogger("time")


@contextmanager
def log_time(message: str, *args: Any, **kwargs: Any) -> Iterator[None]:
    start = time.time()
    try:
        yield
    finally:
        message = f"{message} (took {time.time() - start:.2f}s)"
        time_logger.debug(message, *args, **kwargs)


def remove_path(*paths: FileSystemPath):
    for path in map(Path, paths):
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink(missing_ok=True)


class PurePathError(PydanticTypeError):
    msg_template = "value is not a pure path"


def pure_path_validator(v: Any) -> PurePath:
    if isinstance(v, PurePath):
        return v
    try:
        return PurePath(v)
    except TypeError:
        raise PurePathError()


_VALIDATORS.append((PurePath, [pure_path_validator]))
