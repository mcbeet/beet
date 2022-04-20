from beet import Context, subproject


def beet_default(ctx: Context):
    ctx.require(subproject("beet-nested.yml", package=__name__))


def rename_minecraft(ctx: Context):
    ctx.data["owo"] = ctx.data.pop("minecraft")
