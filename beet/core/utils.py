__all__ = [
    "JsonDict",
    "FileSystemPath",
    "TextComponent",
    "SupportedFormats",
    "Sentinel",
    "SENTINEL_OBJ",
    "dump_json",
    "extra_field",
    "required_field",
    "intersperse",
    "normalize_string",
    "snake_case",
    "VersionNumber",
    "split_version",
    "get_import_string",
    "import_from_string",
    "resolve_packageable_path",
    "local_import_path",
    "log_time",
    "remove_path",
    "format_obj",
    "format_exc",
    "format_validation_error",
    "format_directory",
    "pop_traceback",
    "change_directory",
]


import json
import logging
import os
import re
import shutil
import sys
import time
from contextlib import contextmanager
from dataclasses import field
from importlib import import_module
from importlib.util import find_spec
from pathlib import Path
from traceback import format_exception
from typing import (
    Any,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Protocol,
    Tuple,
    TypeVar,
    Union,
    runtime_checkable,
)

from pydantic import PydanticTypeError, ValidationError
from pydantic.validators import _VALIDATORS  # type: ignore

T = TypeVar("T")


@runtime_checkable
class PathLikeFallback(Protocol):
    def __fspath__(self) -> str:
        ...


JsonDict = Dict[str, Any]
FileSystemPath = Union[str, PathLikeFallback]
TextComponent = Union[str, List[Any], JsonDict]
SupportedFormats = Union[int, List[int], JsonDict]


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


def _raise_required_field() -> Any:
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


VersionNumber = Union[str, int, float, Tuple[Union[str, int], ...]]


def split_version(version: VersionNumber) -> Tuple[int, ...]:
    if isinstance(version, (int, float)):
        version = str(version)
    if isinstance(version, str):
        version = tuple(normalize_string(version).split("_"))
    return tuple(map(int, version))


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


def format_exc(exc: BaseException) -> str:
    return "".join(format_exception(exc.__class__, exc, exc.__traceback__))


def format_obj(obj: Any) -> str:
    module = getattr(obj, "__module__", None)
    name = getattr(obj, "__qualname__", getattr(obj, "__name__", None))
    return f'"{module}.{name}"' if module and name else repr(obj)


def format_validation_error(prefix: str, exc: ValidationError) -> str:
    errors = [
        (
            prefix
            + "".join(
                json.dumps([item]) for item in error["loc"] if item != "__root__"
            ),
            error["msg"]
            if error["msg"][0].isupper()
            else error["msg"][0].capitalize() + error["msg"][1:],
        )
        for error in exc.errors()
    ]
    width = max(len(loc) for loc, _ in errors) + 1
    return "\n".join(
        "{loc:<{width}} => {msg}".format(
            loc=loc,
            width=width,
            msg=msg + "." * (not msg.endswith(".")),
        )
        for loc, msg in errors
    )


def format_directory(directory: FileSystemPath, prefix: str = "") -> Iterator[str]:
    max_entries = 8
    crop_entries = 5

    entries = list(sorted(Path(directory).iterdir()))

    count = len(entries)
    if count > max_entries:
        del entries[crop_entries:]

    indents = ["├─"] * len(entries)
    if count <= max_entries:
        indents[-1] = "└─"

    for indent, entry in zip(indents, entries):
        yield f"{prefix}{indent} {entry.name}"

        if entry.is_dir():
            indent = "│  " if indent == "├─" else "   "
            yield from format_directory(entry, prefix + indent)

    if count > max_entries:
        yield f"{prefix}└─ ... ({count - crop_entries} more entries)"


ExceptionType = TypeVar("ExceptionType", bound=BaseException)


def pop_traceback(exc: ExceptionType, n: int = 1) -> ExceptionType:
    tb = exc.__traceback__
    for _ in range(n):
        tb = getattr(exc.__traceback__, "tb_next", tb)
    return exc.with_traceback(tb)


@contextmanager
def change_directory(directory: Optional[FileSystemPath] = None):
    if not directory:
        yield
        return

    cwd = os.getcwd()
    os.chdir(str(directory))

    try:
        yield
    finally:
        os.chdir(cwd)


class PathObjectError(PydanticTypeError):
    msg_template = "value is not a valid path object"


def path_like_fallback_validator(v: Any) -> PathLikeFallback:
    if isinstance(v, PathLikeFallback):
        return v
    raise PathObjectError()


_VALIDATORS.append((PathLikeFallback, [path_like_fallback_validator]))
