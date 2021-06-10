"""Plugin that formats json files."""


__all__ = [
    "format_json",
]


import json
from typing import Any, Callable, cast

from beet import Context, JsonFileBase, Plugin
from beet.core.utils import JsonDict


def beet_default(ctx: Context):
    config = ctx.meta.get("format_json", cast(JsonDict, {}))

    ensure_ascii = config.get("ensure_ascii", True)
    allow_nan = config.get("allow_nan", True)
    indent = config.get("indent", 2)
    separators = config.get("separators")
    sort_keys = config.get("sort_keys", False)
    final_newline = config.get("final_newline", True)

    if separators:
        separators = (separators[0], separators[1])

    suffix = "\n" if final_newline else ""

    ctx.require(
        format_json(
            lambda content: json.dumps(
                content,
                ensure_ascii=ensure_ascii,
                allow_nan=allow_nan,
                indent=indent,
                separators=separators,
                sort_keys=sort_keys,
            )
            + suffix
        )
    )


def format_json(formatter: Callable[[Any], str]) -> Plugin:
    """Return a plugin that formats json files with the given formatter."""

    def plugin(ctx: Context):
        for pack in ctx.packs:
            for _, json_file in pack.list_files(extend=JsonFileBase[Any]):
                json_file.serializer = formatter
                json_file.text = formatter(json_file.data)

    return plugin
