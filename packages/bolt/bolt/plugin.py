__all__ = [
    "beet_default",
]


from beet import Context

from .runtime import Runtime


def beet_default(ctx: Context):
    ctx.inject(Runtime)
