"""Plugin that adds a header to functions automatically."""


__all__ = [
    "function_header",
]


from typing import Iterable, Optional, cast

from beet import Context, Plugin
from beet.core.utils import JsonDict


def beet_default(ctx: Context):
    config = ctx.meta.get("function_header", cast(JsonDict, {}))

    match = config.get("match", ())
    template = config.get("template", "function_header.mcfunction")

    ctx.require(function_header(match, template))


def function_header(
    match: Iterable[str] = (),
    template: Optional[str] = "function_header.mcfunction",
) -> Plugin:
    """Return a plugin that adds a header to functions automatically."""

    def plugin(ctx: Context):
        if not template:
            return

        for path in ctx.data.functions.match(*match):
            with ctx.override(render_path=path, render_group="functions"):
                header = ctx.template.render(template)
            function = ctx.data.functions[path]
            function.text = header + function.text

    return plugin
