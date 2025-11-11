from beet import Context, Function


def beet_default(ctx: Context):
    ctx.data["demo:bar"] = Function(["say bar"])
