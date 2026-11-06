"""Plugin that adds a header to functions automatically."""

__all__ = [
    "FunctionHeaderOptions",
    "function_header",
]


from beet import Context, Function, PluginOptions, configurable


class FunctionHeaderOptions(PluginOptions):
    match: list[str] = []
    template: str | None = "function_header.mcfunction"


def beet_default(ctx: Context):
    ctx.require(function_header)


@configurable(validator=FunctionHeaderOptions)
def function_header(ctx: Context, opts: FunctionHeaderOptions):
    """Plugin that adds a header to functions automatically."""
    if not opts.template:
        return

    for path, function in ctx.data.all(*opts.match, extend=Function):
        with ctx.override(render_path=path, render_group="functions"):
            header = ctx.template.render(opts.template)
        function.text = header + function.text
