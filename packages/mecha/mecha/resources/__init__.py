__all__ = [
    "get_wiki_argument_types",
    "get_wiki_examples",
]


import json
from importlib.resources import read_text
from typing import Dict, List

from beet import Function


def get_wiki_argument_types() -> Dict[str, List[str]]:
    return json.loads(read_text("mecha.resources", "wiki_argument_types.json"))


def get_wiki_examples() -> Function:
    return Function(read_text("mecha.resources", "wiki_examples.mcfunction"))
