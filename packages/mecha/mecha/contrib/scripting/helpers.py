__all__ = [
    "get_scripting_helpers",
]


from dataclasses import replace
from typing import Any, Dict, Union, cast

from tokenstream import set_location

from mecha import (
    AstBool,
    AstChildren,
    AstJson,
    AstLiteral,
    AstMessage,
    AstNumber,
    AstResourceLocation,
    AstSelector,
    AstString,
    AstTime,
)
from mecha.ast import AstNbt, AstRange
from mecha.utils import string_to_number


def get_scripting_helpers() -> Dict[str, Any]:
    """Return a collection of helpers used by the generated code."""
    return {
        "replace": replace,
        "missing": object(),
        "children": AstChildren,
        "set_location": set_location,
        "get_attribute": get_attribute,
        "convert_literal": convert_literal,
        "convert_bool": convert_bool,
        "convert_numeric": convert_numeric,
        "convert_time": convert_time,
        "convert_string": convert_string,
        "convert_json": convert_json,
        "convert_nbt": convert_nbt,
        "convert_range": convert_range,
        "convert_resource_location": convert_resource_location,
        "convert_message": convert_message,
    }


def get_attribute(obj: Any, attr: str):
    try:
        return getattr(obj, attr)
    except AttributeError:
        pass
    return obj[attr]


def convert_literal(obj: Any) -> AstLiteral:
    return AstLiteral(value=str(obj))


def convert_bool(obj: Any) -> AstBool:
    return AstBool(value=bool(obj))


def convert_numeric(obj: Any) -> AstNumber:
    if isinstance(obj, str):
        obj = string_to_number(obj)
    return AstNumber(value=obj)


def convert_time(obj: Any) -> AstTime:
    return AstTime.from_value(obj)


def convert_string(obj: Any) -> AstString:
    return AstString(value=str(obj))


def convert_json(obj: Any) -> AstJson:
    return AstJson.from_value(obj)


def convert_nbt(obj: Any) -> AstNbt:
    return AstNbt.from_value(obj)


def convert_range(obj: Any) -> AstRange:
    return AstRange.from_value(obj)


def convert_resource_location(obj: Any) -> AstResourceLocation:
    return AstResourceLocation.from_value(str(obj))


def convert_message(obj: Any) -> AstMessage:
    fragments = AstChildren([AstLiteral(value=str(obj))])
    return AstMessage(
        fragments=cast(AstChildren[Union[AstLiteral, AstSelector]], fragments)
    )
