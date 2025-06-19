from beet import Context


def beet_default(ctx: Context):
    all = [
        f"{ctx.data.mcmeta.data}",
        f"{ctx.assets.mcmeta.data}",
    ]
    ctx.meta["pytest"] = "\n".join(all) + "\n"
