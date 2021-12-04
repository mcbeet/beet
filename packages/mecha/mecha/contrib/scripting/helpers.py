__all__ = [
    "get_scripting_helpers",
]


import re
from dataclasses import replace
from typing import Any, Dict, Union, cast

from beet.core.utils import JsonDict
from tokenstream import set_location

from mecha import (
    AstBool,
    AstChildren,
    AstJson,
    AstLiteral,
    AstNode,
    AstNumber,
    AstString,
)
from mecha.ast import AstMessage, AstSelector

WORD_REGEX = re.compile(r"[0-9A-Za-z_\.\+\-]+")


def get_scripting_helpers() -> Dict[str, Any]:
    """Return a collection of helpers used by the generated code."""
    return {
        "replace": replace,
        "missing": object(),
        "children": AstChildren,
        "set_location": set_location,
        "get_attribute": get_attribute,
        "convert:brigadier:bool": convert_bool,
        "convert:brigadier:double": convert_float,
        "convert:brigadier:float": convert_float,
        "convert:brigadier:integer": convert_int,
        "convert:brigadier:long": convert_int,
        "convert:brigadier:string": convert_string,
        "convert:minecraft:component": convert_json,
        "convert:minecraft:message": convert_message,
    }


def get_attribute(obj: Any, attr: str):
    try:
        return getattr(obj, attr)
    except AttributeError:
        pass
    return obj[attr]


def convert_bool(obj: Any, properties: JsonDict) -> AstBool:
    return AstBool(value=bool(obj))


def convert_float(obj: Any, properties: JsonDict) -> AstNumber:
    return AstNumber(value=float(obj))


def convert_int(obj: Any, properties: JsonDict) -> AstNumber:
    return AstNumber(value=int(obj))


def convert_string(obj: Any, properties: JsonDict) -> AstNode:
    value = str(obj)
    string_type = properties["type"]

    if string_type == "greedy":
        return AstLiteral(value=value)
    elif string_type == "word":
        if WORD_REGEX.match(value):
            return AstLiteral(value=value)
        raise ValueError("Invalid word {value!r}.")
    elif string_type == "phrase":
        return AstString(value=value)

    raise ValueError(f"Invalid string type {string_type!r}.")


def convert_json(obj: Any, properties: JsonDict) -> AstJson:
    return AstJson.from_value(obj)


def convert_message(obj: Any, properties: JsonDict) -> AstMessage:
    fragments = AstChildren([AstLiteral(value=str(obj))])
    return AstMessage(
        fragments=cast(AstChildren[Union[AstLiteral, AstSelector]], fragments)
    )
