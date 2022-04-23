from beet import Context, subproject


def beet_default(ctx: Context):
    ctx.require(subproject(f"@{__name__}/beet-nested.yml"))


def rename_minecraft(ctx: Context):
    ctx.data["owo"] = ctx.data.pop("minecraft")
