__all__ = [
    "LazyFormat",
    "stable_int_hash",
    "stable_hash",
    "ensure_builtins",
    "iter_options",
    "eval_option",
    "default_option",
    "apply_option",
]


import json
import re
import sys
from copy import copy
from importlib.metadata import EntryPoint, entry_points
from typing import (
    Any,
    Callable,
    Iterable,
    List,
    Literal,
    Mapping,
    Sequence,
    Tuple,
    cast,
)

FNV_32_INIT = 0x811C9DC5
FNV_64_INIT = 0xCBF29CE484222325
FNV_32_PRIME = 0x01000193
FNV_64_PRIME = 0x100000001B3
HASH_ALPHABET = "123456789abcdefghijkmnopqrstuvwxyz"


OPTION_KEY_REGEX = re.compile(r"\s*\[\s*(-?\d+)\s*\]\s*|\s*\[\s*\]\s*|\s*(\w+)\s*")


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
        return fnva(value, FNV_32_INIT, FNV_32_PRIME, 2**size)
    else:
        return fnva(value, FNV_64_INIT, FNV_64_PRIME, 2**size)


def stable_hash(value: Any, short: bool = False) -> str:
    result = stable_int_hash(value, size=32 if short else 64)
    return encode_with_alphabet(result, HASH_ALPHABET)


def encode_with_alphabet(value: int, alphabet: str) -> str:
    indices: List[int] = []
    while value:
        value, i = divmod(value, len(alphabet))
        indices.append(i)
    return "".join(alphabet[i] for i in reversed(indices))


def ensure_builtins(value: Any) -> Any:
    try:
        return json.loads(json.dumps(value))
    except Exception:
        raise TypeError(value) from None


def select_entry_points(group: str) -> Tuple[EntryPoint, ...]:
    eps: Any = entry_points()
    if sys.version_info >= (3, 10):
        return eps.select(group=group)
    else:
        return eps.get(group, ())


def iter_options(options: Any) -> Iterable[str]:
    if isinstance(options, str):
        yield from options.splitlines()
    elif isinstance(options, Mapping):
        yield from iter_options(options.get("overrides", []))  # type: ignore
    elif isinstance(options, Sequence):
        for option in options:  # type: ignore
            yield from iter_options(option)


def eval_option(option: str) -> Any:
    option = option.strip()

    if option.startswith("{"):
        return json.loads(option)

    key, sep, value = option.partition("=")
    matches = list(OPTION_KEY_REGEX.finditer(key))

    if sep:
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            value = value.strip()
    elif matches:
        value = True
    else:
        value = cast(Mapping[Any, Any], {})

    for m in matches[::-1]:
        if m[1]:
            value = {int(m[1]): value}
        elif m[2]:
            value = {m[2]: value}
        else:
            value = [value]

    return value


def default_option(option: Any) -> Any:
    if isinstance(option, Mapping):
        if option and all(isinstance(k, int) for k in option):  # type: ignore
            return []
        return {}
    if isinstance(option, Sequence) and not isinstance(option, str):
        return []
    return None


def apply_option(result: Any, option: Any) -> Any:
    if isinstance(option, Mapping):
        default = default_option(option)

        if (
            isinstance(default, dict)
            and not isinstance(result, Mapping)
            or isinstance(default, list)
            and not (isinstance(result, Sequence) and not isinstance(result, str))
        ):
            result = default
        else:
            result = copy(result)  # type: ignore

        for key, value in cast(Mapping[Any, Any], option).items():
            if isinstance(key, int):
                if key >= len(result):
                    result.append(apply_option(default_option(value), value))
                    continue
                key = (key + len(result)) % len(result)

            try:
                current = result[key]
            except LookupError:
                current = default_option(value)

            result[key] = apply_option(current, value)

    elif isinstance(option, Sequence) and not isinstance(option, str):
        option = [apply_option(default_option(value), value) for value in option]  # type: ignore

        if isinstance(result, Sequence) and not isinstance(result, str):
            result = [*result, *option]
        elif result is not None:
            result = [result, *option]
        else:
            result = [*option]

    else:
        result = option

    return result
