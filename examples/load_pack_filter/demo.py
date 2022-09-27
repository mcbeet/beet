from beet import Context


def beet_default(ctx: Context):
    ctx.data.filter["block"].append({"namespace": "thing"})
