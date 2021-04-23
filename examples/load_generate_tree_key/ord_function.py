from beet import Context


def beet_default(ctx: Context):
    ctx.template.expose("ord", ord)
