from beet import Context


def beet_default(ctx: Context):
    ctx.data.description = ["override for ", {"text": "data pack", "color": "red"}]
