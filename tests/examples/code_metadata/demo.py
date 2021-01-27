from beet import Context, Function


def beet_default(ctx: Context):
    ctx.project_name = "demo"
    ctx.project_description = "The description of my project"
    ctx.project_author = "Example"
    ctx.project_version = "1.7.4"

    ctx.data["demo:foo"] = Function(ctx.template.render("foo.mcfunction"))
