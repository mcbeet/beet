from beet import Context


def beet_default(ctx: Context):
    all = [
        f"{ctx.data.name}",
        f"{ctx.data.description}",
        f"{ctx.data.pack_format}",
        f"{ctx.data.supported_formats}",
        f"{ctx.assets.name}",
        f"{ctx.assets.description}",
        f"{ctx.assets.pack_format}",
        f"{ctx.assets.supported_formats}",
    ]
    ctx.meta["pytest"] = "\n".join(all) + "\n"
