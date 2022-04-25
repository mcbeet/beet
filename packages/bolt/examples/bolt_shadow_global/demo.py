from beet import Context

from bolt import Runtime


def beet_default(ctx: Context):
    runtime = ctx.inject(Runtime)
    runtime.expose("max", lambda *args: args)
