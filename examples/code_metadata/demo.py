from beet import Context, Function


def beet_default(ctx: Context):
    ctx.data["demo:foo"] = Function(
        ctx.template.render(
            "foo.mcfunction",
            id=ctx.project_id,
            name=ctx.project_name,
            description=ctx.project_description,
            author=ctx.project_author,
            version=ctx.project_version,
        )
    )
