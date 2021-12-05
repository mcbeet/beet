__all__ = [
    "get_scripting_helpers",
]


from dataclasses import replace
from functools import wraps
from typing import Any, Callable, Dict, Union, cast

from tokenstream import set_location

from mecha import (
    AstBool,
    AstChildren,
    AstJson,
    AstLiteral,
    AstMessage,
    AstNbt,
    AstNode,
    AstNumber,
    AstRange,
    AstResourceLocation,
    AstSelector,
    AstString,
    AstTime,
)
from mecha.utils import string_to_number

from .utils import internal


def get_scripting_helpers() -> Dict[str, Any]:
    """Return a collection of helpers used by the generated code."""
    return {
        "replace": replace,
        "missing": object(),
        "children": AstChildren,
        "get_attribute": get_attribute,
        "interpolate_literal": converter(interpolate_literal),
        "interpolate_bool": converter(interpolate_bool),
        "interpolate_numeric": converter(interpolate_numeric),
        "interpolate_time": converter(interpolate_time),
        "interpolate_string": converter(interpolate_string),
        "interpolate_json": converter(interpolate_json),
        "interpolate_nbt": converter(interpolate_nbt),
        "interpolate_range": converter(interpolate_range),
        "interpolate_resource_location": converter(interpolate_resource_location),
        "interpolate_message": converter(interpolate_message),
    }


@internal
def get_attribute(obj: Any, attr: str):
    try:
        return getattr(obj, attr)
    except AttributeError as exc:
        try:
            return obj[attr]
        except (TypeError, LookupError):
            raise exc from None


def converter(f: Callable[[Any], AstNode]) -> Callable[[Any, AstNode], AstNode]:
    @internal
    @wraps(f)
    def wrapper(obj: Any, node: AstNode) -> AstNode:
        return set_location(f(obj), node)

    return wrapper


def interpolate_literal(obj: Any) -> AstLiteral:
    return AstLiteral(value=str(obj))


def interpolate_bool(obj: Any) -> AstBool:
    return AstBool(value=bool(obj))


def interpolate_numeric(obj: Any) -> AstNumber:
    if isinstance(obj, str):
        obj = string_to_number(obj)
    return AstNumber(value=obj)


def interpolate_time(obj: Any) -> AstTime:
    return AstTime.from_value(obj)


def interpolate_string(obj: Any) -> AstString:
    return AstString(value=str(obj))


def interpolate_json(obj: Any) -> AstJson:
    return AstJson.from_value(obj)


def interpolate_nbt(obj: Any) -> AstNbt:
    return AstNbt.from_value(obj)


def interpolate_range(obj: Any) -> AstRange:
    return AstRange.from_value(obj)


def interpolate_resource_location(obj: Any) -> AstResourceLocation:
    return AstResourceLocation.from_value(str(obj))


def interpolate_message(obj: Any) -> AstMessage:
    fragments = AstChildren([AstLiteral(value=str(obj))])
    return AstMessage(
        fragments=cast(AstChildren[Union[AstLiteral, AstSelector]], fragments)
    )
