"""Plugin that adds a header to functions automatically."""


__all__ = [
    "FunctionHeaderOptions",
    "function_header",
]


from typing import List, Optional

from beet import Context, Function, PluginOptions, configurable


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

    for function, (_, path) in ctx.select(match=opts.match, extend=Function).items():
        with ctx.override(render_path=path, render_group="functions"):
            header = ctx.template.render(opts.template)
        function.text = header + function.text
