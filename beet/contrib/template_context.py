"""Plugin that exposes the beet context in templates"""


from beet import Context


def beet_default(ctx: Context):
    ctx.template.env.globals["ctx"] = ctx
