__all__ = [
    "LazyFormat",
    "stable_int_hash",
    "stable_hash",
    "format_obj",
    "format_exc",
    "format_validation_error",
    "import_from_string",
    "locate_minecraft",
    "ensure_builtins",
]


import json
import os
import platform
import struct
from importlib import import_module
from pathlib import Path
from traceback import format_exception
from typing import Any, Callable, List, Literal, Optional

from base58 import b58encode
from fnvhash import fnv1a_32, fnv1a_64
from pydantic import ValidationError

HASH_ALPHABET = b"123456789abcdefghijkmnopqrstuvwxyz"


class LazyFormat:
    def __init__(self, func: Callable[[], Any]):
        self.func = func

    def __format__(self, format_spec: str) -> str:
        return self.func().__format__(format_spec)


def stable_int_hash(value: Any, size: Literal[32, 64] = 64) -> int:
    if callable(value):
        value = value()
    if not isinstance(value, bytes):
        value = str(value).encode()
    hasher = fnv1a_32 if size == 32 else fnv1a_64
    return hasher(value)


def stable_hash(value: Any, short: bool = False) -> str:
    result = stable_int_hash(value, size=32 if short else 64)
    fmt = ">I" if short else ">Q"
    return b58encode(struct.pack(fmt, result), HASH_ALPHABET).decode()


def format_exc(exc: BaseException) -> str:
    return "".join(format_exception(exc.__class__, exc, exc.__traceback__))


def format_obj(obj: Any) -> str:
    module = getattr(obj, "__module__", None)
    name = getattr(obj, "__qualname__", None)
    return repr(f"{module}.{name}") if module and name else repr(obj)


def format_validation_error(prefix: str, exc: ValidationError) -> str:
    errors = [
        (
            prefix + "".join(json.dumps([item]) for item in error["loc"]),
            error["msg"].capitalize(),
        )
        for error in exc.errors()
    ]
    width = max(len(loc) for loc, _ in errors) + 1
    return "\n".join(
        "{loc:<{width}} => {msg}.".format(loc=loc, width=width, msg=msg)
        for loc, msg in errors
    )


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


def locate_minecraft() -> Optional[Path]:
    locations = [
        Path(path) for path in os.environ.get("MINECRAFT_PATH", "").split(":") if path
    ]
    system = platform.system()

    if system == "Linux":
        locations.append(Path("~/.minecraft").expanduser())
        locations.append(
            Path("~/.var/app/com.mojang.Minecraft/data/minecraft").expanduser()
        )
    elif system == "Darwin":
        locations.append(Path("~/Library/Application Support/minecraft").expanduser())
    elif system == "Windows":
        locations.append(Path(os.path.expandvars(r"%APPDATA%\.minecraft")))

    return next((path.resolve() for path in locations if path and path.is_dir()), None)


def ensure_builtins(value: Any) -> Any:
    try:
        return json.loads(json.dumps(value))
    except Exception:
        raise TypeError(value) from None
