from beet import Context, Function


def beet_default(ctx: Context):
    ctx.generate(Function("say 123\nfunction demo:thing:\n    say 456\n"))
