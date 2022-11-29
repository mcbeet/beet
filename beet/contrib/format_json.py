"""Plugin that formats json files."""


__all__ = [
    "FormatJsonOptions",
    "format_json",
]


import json
from typing import Any, Callable, Optional, Tuple, Union

from beet import Context, JsonFileBase, PluginOptions, configurable


class FormatJsonOptions(PluginOptions):
    ensure_ascii: bool = True
    allow_nan: bool = True
    indent: Union[int, str, None] = 2
    separators: Optional[Tuple[str, str]] = None
    sort_keys: bool = False
    final_newline: bool = True


def get_formatter(
    formatter: Optional[Callable[[Any], str]] = None,
    **kwargs: Any,
) -> Callable[[Any], str]:
    if callable(formatter):
        return formatter

    opts = FormatJsonOptions(**kwargs)

    suffix = "\n" if opts.final_newline else ""

    return (
        lambda content: json.dumps(
            content,
            ensure_ascii=opts.ensure_ascii,
            allow_nan=opts.allow_nan,
            indent=opts.indent,
            separators=opts.separators,
            sort_keys=opts.sort_keys,
        )
        + suffix
    )


def beet_default(ctx: Context):
    ctx.require(format_json)


@configurable(validator=get_formatter)
def format_json(ctx: Context, formatter: Callable[[Any], str]):
    """Plugin that formats json files with the given formatter."""
    for pack in ctx.packs:
        for _, json_file in pack.list_files(extend=JsonFileBase[Any]):
            json_file.encoder = formatter
            json_file.text = formatter(json_file.data)
