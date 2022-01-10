__all__ = [
    "get_scripting_helpers",
]


from dataclasses import replace
from functools import wraps
from importlib import import_module
from typing import Any, Callable, Dict

from tokenstream import set_location

from mecha import (
    AstBool,
    AstChildren,
    AstColor,
    AstCoordinate,
    AstGamemode,
    AstGreedy,
    AstJson,
    AstMessage,
    AstNbt,
    AstNode,
    AstNumber,
    AstObjective,
    AstObjectiveCriteria,
    AstRange,
    AstResourceLocation,
    AstSortOrder,
    AstString,
    AstSwizzle,
    AstTeam,
    AstTime,
    AstVector2,
    AstVector3,
    AstWord,
)

from .utils import internal


def get_scripting_helpers() -> Dict[str, Any]:
    """Return a collection of helpers used by the generated code."""
    return {
        "replace": replace,
        "missing": object(),
        "children": AstChildren,
        "get_attribute": get_attribute,
        "import_module": python_import_module,
        "interpolate_bool": converter(AstBool.from_value),
        "interpolate_numeric": converter(AstNumber.from_value),
        "interpolate_coordinate": converter(AstCoordinate.from_value),
        "interpolate_time": converter(AstTime.from_value),
        "interpolate_word": converter(AstWord.from_value),
        "interpolate_phrase": converter(AstString.from_value),
        "interpolate_greedy": converter(AstGreedy.from_value),
        "interpolate_json": converter(AstJson.from_value),
        "interpolate_nbt": converter(AstNbt.from_value),
        "interpolate_range": converter(AstRange.from_value),
        "interpolate_resource_location": converter(AstResourceLocation.from_value),
        "interpolate_objective": converter(AstObjective.from_value),
        "interpolate_objective_criteria": converter(AstObjectiveCriteria.from_value),
        "interpolate_swizzle": converter(AstSwizzle.from_value),
        "interpolate_team": converter(AstTeam.from_value),
        "interpolate_color": converter(AstColor.from_value),
        "interpolate_sort_order": converter(AstSortOrder.from_value),
        "interpolate_gamemode": converter(AstGamemode.from_value),
        "interpolate_message": converter(AstMessage.from_value),
        "interpolate_vec2": converter(AstVector2.from_value),
        "interpolate_vec3": converter(AstVector3.from_value),
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


@internal
def python_import_module(name: str):
    try:
        return import_module(name)
    except Exception as exc:
        tb = exc.__traceback__
        tb = tb.tb_next.tb_next  # type: ignore
        while tb and tb.tb_frame.f_code.co_filename.startswith("<frozen importlib"):
            tb = tb.tb_next
        raise exc.with_traceback(tb)


def converter(f: Callable[[Any], AstNode]) -> Callable[[Any, AstNode], AstNode]:
    internal(f)

    @internal
    @wraps(f)
    def wrapper(obj: Any, node: AstNode) -> AstNode:
        return set_location(f(obj), node)

    return wrapper
