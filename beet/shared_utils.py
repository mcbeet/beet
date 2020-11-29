# pyright: strict


__all__ = [
    "JsonDict",
    "FileSystemPath",
    "dump_json",
    "extra_field",
    "unreachable",
]


import json
import os
from dataclasses import field
from typing import Any, Dict, NoReturn, Union

JsonDict = Dict[str, Any]
FileSystemPath = Union[str, os.PathLike]


def dump_json(value: Any) -> str:
    return json.dumps(value, indent=2) + "\n"


def extra_field(**kwargs: Any) -> Any:
    return field(repr=False, hash=False, compare=False, **kwargs)


def unreachable() -> NoReturn:
    assert False
