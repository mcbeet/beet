"""Plugin that adds a header to functions automatically."""


from beet import Context


def beet_default(ctx: Context):
    config = ctx.meta.get("function_header", {})
    patterns = config.get("match", [])
    template = config.get("template", "function_header.mcfunction")

    for path in ctx.data.functions.match(*patterns):
        with ctx.override(render_path=path, render_group="functions"):
            header = ctx.template.render(template)
        function = ctx.data.functions[path]
        function.content = header + function.text
