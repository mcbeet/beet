__all__ = [
    "beet_default",
]


from beet import Context

from .api import Mecha


def beet_default(ctx: Context):
    mc = ctx.inject(Mecha)

    mc.compile(together=ctx.packs, report=mc.diagnostics)
