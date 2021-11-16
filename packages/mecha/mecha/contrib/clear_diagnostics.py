"""Plugin that clears diagnostics."""


from beet import Context

from mecha import Mecha


def beet_default(ctx: Context):
    mc = ctx.inject(Mecha)
    mc.diagnostics.clear()
