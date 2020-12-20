from beet import Context, Function


def beet_default(ctx: Context):
    ctx.template.add_package(__name__)
    ctx.data["demo:hello"] = Function(
        ctx.template.render("demo/hello.mcfunction", message="hello")
    )
