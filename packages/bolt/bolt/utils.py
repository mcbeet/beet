__all__ = [
    "rewrite_traceback",
    "fake_traceback",
    "suggest_typo",
    "load_pickle",
    "dump_pickle",
    "internal",
    "INTERNAL_CODE",
]


import pickle
from bisect import bisect
from difflib import get_close_matches
from types import CodeType, TracebackType
from typing import Any, Iterable, List, Optional, Set, TypeVar

from beet import Container
from beet.core.utils import FileSystemPath
from mecha.utils import string_to_number

T = TypeVar("T")


INTERNAL_CODE: Set[CodeType] = {
    string_to_number.__code__,
    Container[Any, Any].__getitem__.__code__,
}


def internal(f: T) -> T:
    INTERNAL_CODE.add(f.__code__)  # type: ignore
    return f


def rewrite_traceback(exc: Exception) -> Exception:
    tb = exc.__traceback__ and exc.__traceback__.tb_next

    stack: List[TracebackType] = []

    while tb is not None:
        if tb.tb_frame.f_code in INTERNAL_CODE:
            tb = tb.tb_next
            continue

        line_numbers = tb.tb_frame.f_globals.get("_bolt_lineno")

        if line_numbers:
            n1, n2 = line_numbers
            lineno = n2[bisect(n1, tb.tb_lineno) - 1]
            stack.append(fake_traceback(exc, tb, lineno))
        else:
            stack.append(tb)

        tb = tb.tb_next

    tb_next = None

    for tb in reversed(stack):
        tb.tb_next = tb_next
        tb_next = tb

    return exc.with_traceback(tb)


def fake_traceback(exc: Exception, tb: TracebackType, lineno: int) -> TracebackType:  # type: ignore
    name = tb.tb_frame.f_code.co_name
    filename = tb.tb_frame.f_globals["__file__"]

    if name == "<module>":
        name = tb.tb_frame.f_globals.get("__name__")

    code = compile("\n" * (lineno - 1) + "raise _bolt_exc", filename, "exec")

    if name:
        code = code.replace(co_name=name)

    try:
        exec(code, {"_bolt_exc": exc})
    except Exception as exc:
        return exc.__traceback__.tb_next  # type: ignore


def suggest_typo(wrong: str, possibilities: Iterable[str]) -> Optional[str]:
    cutoff = 0.6 if len(wrong) < 3 else 0.7

    if matches := get_close_matches(wrong, possibilities, cutoff=cutoff):
        matches = [f'"{m}"' for m in matches]

        if len(matches) == 1:
            return matches[0]
        else:
            *head, before_last, last = matches
            return ", ".join(head + [f"{before_last} or {last}"])

    return None


def load_pickle(path: FileSystemPath) -> Any:
    with open(path, "rb") as f:
        return pickle.load(f)


def dump_pickle(path: FileSystemPath, value: Any):
    with open(path, "wb") as f:
        return pickle.dump(value, f, protocol=pickle.HIGHEST_PROTOCOL)
