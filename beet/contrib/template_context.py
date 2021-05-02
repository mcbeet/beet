"""Plugin that exposes the beet context in templates"""


from beet import Context


def beet_default(ctx: Context):
    ctx.template.globals["ctx"] = ctx
