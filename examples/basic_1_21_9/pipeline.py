from beet import Context


def beet_default(ctx: Context):
    print(ctx.assets.min_format)
    ctx.assets.min_format = 40
    print(ctx.assets.min_format)
