__all__ = [
    "LazyFormat",
    "stable_int_hash",
    "stable_hash",
    "format_obj",
    "format_exc",
    "format_validation_error",
    "ensure_builtins",
]


import json
import struct
from traceback import format_exception
from typing import Any, Callable, Literal

from base58 import b58encode
from pydantic import ValidationError

FNV_32_INIT = 0x811C9DC5
FNV_64_INIT = 0xCBF29CE484222325
FNV_32_PRIME = 0x01000193
FNV_64_PRIME = 0x100000001B3
HASH_ALPHABET = b"123456789abcdefghijkmnopqrstuvwxyz"


class LazyFormat:
    def __init__(self, func: Callable[[], Any]):
        self.func = func

    def __format__(self, format_spec: str) -> str:
        return self.func().__format__(format_spec)


def fnva(data: bytes, hval_init: int, fnv_prime: int, fnv_size: int):
    hval = hval_init
    for byte in data:
        hval = hval ^ byte
        hval = (hval * fnv_prime) % fnv_size
    return hval


def stable_int_hash(value: Any, size: Literal[32, 64] = 64) -> int:
    if callable(value):
        value = value()
    if not isinstance(value, bytes):
        value = str(value).encode()

    if size == 32:
        return fnva(value, FNV_32_INIT, FNV_32_PRIME, 2 ** size)
    else:
        return fnva(value, FNV_64_INIT, FNV_64_PRIME, 2 ** size)


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


def ensure_builtins(value: Any) -> Any:
    try:
        return json.loads(json.dumps(value))
    except Exception:
        raise TypeError(value) from None
