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
    "resolve_packageable_path",
    "local_import_path",
    "log_time",
    "remove_path",
]


import json
import logging
import re
import shutil
import sys
import time
from contextlib import contextmanager
from dataclasses import field
from importlib import import_module
from importlib.util import find_spec
from pathlib import Path, PurePath
from typing import (
    Any,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Protocol,
    TypeVar,
    Union,
    runtime_checkable,
)

from pydantic import PydanticTypeError
from pydantic.validators import _VALIDATORS  # type: ignore

T = TypeVar("T")


@runtime_checkable
class PathLikeFallback(Protocol):
    def __fspath__(self) -> str:
        ...


JsonDict = Dict[str, Any]
FileSystemPath = Union[str, PurePath, PathLikeFallback]
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


def resolve_packageable_path(value: T) -> Union[T, Path]:
    value_str = str(value)

    if value_str.startswith("@"):
        if parts := Path(value_str[1:]).parts:
            package_name, *parts = parts

            spec = find_spec(package_name)

            if not spec:
                msg = f'Couldn\'t resolve "{value_str}". No package named "{package_name}".'
                raise ValueError(msg) from None

            if not spec.origin:
                msg = f'Couldn\'t resolve "{value_str}". Package "{package_name}" doesn\'t have a corresponding file origin.'
                raise ValueError(msg) from None

            if not spec.origin.endswith("__init__.py"):
                msg = f'Couldn\'t resolve "{value_str}". The resolved module "{package_name}" does not refer to a package.'
                raise ValueError(msg) from None

            return Path(spec.origin).parent / Path(*parts)

        else:
            raise ValueError(f'Blank package reference "{value}".')

    return value


@contextmanager
def local_import_path(sys_path_entry: str):
    already_loaded = set(sys.modules)

    not_in_path = sys_path_entry not in sys.path
    if not_in_path:
        sys.path.append(sys_path_entry)

    try:
        yield
    finally:
        if not_in_path:
            sys.path.remove(sys_path_entry)

        imported_modules = [
            name
            for name, module in sys.modules.items()
            if name not in already_loaded
            and (filename := getattr(module, "__file__", None))
            and "site-packages" not in filename
            and filename.startswith(sys_path_entry)
        ]

        for name in imported_modules:
            del sys.modules[name]


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


class PathObjectError(PydanticTypeError):
    msg_template = "value is not a valid path object"


def pure_path_validator(v: Any) -> PurePath:
    if isinstance(v, PurePath):
        return v
    try:
        return PurePath(v)
    except TypeError:
        raise PathObjectError()


def path_like_fallback_validator(v: Any) -> PathLikeFallback:
    if isinstance(v, PathLikeFallback):
        return v
    raise PathObjectError()


_VALIDATORS.append((PurePath, [pure_path_validator]))
_VALIDATORS.append((PathLikeFallback, [path_like_fallback_validator]))
