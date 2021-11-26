__all__ = [
    "get_argument_examples",
    "get_command_examples",
    "get_multiline_command_examples",
    "get_scripting_examples",
]


import json
from importlib.resources import read_text
from typing import List

from beet import Function
from beet.core.utils import JsonDict


def get_argument_examples() -> JsonDict:
    return json.loads(read_text("mecha.resources", "argument_examples.json"))


def get_command_examples() -> Function:
    return Function(read_text("mecha.resources", "command_examples.mcfunction"))


def get_multiline_command_examples() -> Function:
    return Function(
        read_text("mecha.resources", "multiline_command_examples.mcfunction")
    )


def get_scripting_examples() -> List[Function]:
    return [
        Function(source)
        for source in read_text(
            "mecha.resources", "scripting_examples.mcfunction"
        ).split("###\n")
    ]
