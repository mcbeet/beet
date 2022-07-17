__all__ = [
    "bolt",
    "beet_default",
]


from beet import Context, ListOption, configurable
from pydantic import BaseModel

from .runtime import Runtime


class BoltOptions(BaseModel):
    entrypoint: ListOption[str] = ListOption()


def beet_default(ctx: Context):
    ctx.require(bolt)


@configurable(validator=BoltOptions)
def bolt(ctx: Context, opts: BoltOptions):
    """Plugin for configuring bolt."""
    runtime = ctx.inject(Runtime)
    runtime.evaluate.add_entrypoint(opts.entrypoint.entries())
