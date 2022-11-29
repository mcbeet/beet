"""Plugin that adds a header to functions automatically."""


__all__ = [
    "FunctionHeaderOptions",
    "function_header",
]


from typing import List, Optional

from beet import Context, PluginOptions, configurable


class FunctionHeaderOptions(PluginOptions):
    match: List[str] = []
    template: Optional[str] = "function_header.mcfunction"


def beet_default(ctx: Context):
    ctx.require(function_header)


@configurable(validator=FunctionHeaderOptions)
def function_header(ctx: Context, opts: FunctionHeaderOptions):
    """Plugin that adds a header to functions automatically."""
    if not opts.template:
        return

    for path in ctx.data.functions.match(*opts.match):
        with ctx.override(render_path=path, render_group="functions"):
            header = ctx.template.render(opts.template)
        function = ctx.data.functions[path]
        function.text = header + function.text
