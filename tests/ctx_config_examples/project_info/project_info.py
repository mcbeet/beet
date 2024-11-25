from beet import Context


def beet_default(ctx: Context):
    all = [
        f"{ctx.minecraft_version}",
        f"{ctx.project_author}",
        f"{ctx.project_description}",
        f"{ctx.project_id}",
        f"{ctx.project_name}",
        f"{ctx.project_version}",
    ]
    ctx.meta["pytest"] = "\n".join(all) + "\n"
