__all__ = [
    "FileSystemPath",
    "ensure_optional_value",
    "extra_field",
    "import_from_string",
]


import os
from dataclasses import field
from importlib import import_module
from typing import Optional, Union, TypeVar, Any


FileSystemPath = Union[str, os.PathLike]


T = TypeVar("T")


def ensure_optional_value(arg: Optional[T]) -> T:
    assert arg is not None
    return arg


def extra_field(**kwargs) -> Any:
    return field(**kwargs, repr=False)


def import_from_string(dotted_path: str, default_member: str = None) -> Any:
    try:
        module = import_module(dotted_path)
    except ImportError:
        if "." not in dotted_path:
            raise
        dotted_path, _, default_member = dotted_path.rpartition(".")
        module = import_module(dotted_path)
    return getattr(module, default_member) if default_member else module
