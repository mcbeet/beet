from beet import Context


def beet_default(ctx: Context):
    ctx.template.add_package(__name__)
