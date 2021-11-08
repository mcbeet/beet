"""Plugin that loads data packs and resource packs."""


__all__ = [
    "LoadOptions",
    "load",
]


from glob import glob
from typing import List

from pydantic import BaseModel

from beet import Context, configurable


class LoadOptions(BaseModel):
    resource_pack: List[str] = []
    data_pack: List[str] = []


def beet_default(ctx: Context):
    ctx.require(load)


@configurable(validator=LoadOptions)
def load(ctx: Context, opts: LoadOptions):
    """Plugin that loads data packs and resource packs."""
    for config, pack in zip([opts.resource_pack, opts.data_pack], ctx.packs):
        for pattern in config:
            for path in glob(str(ctx.directory / pattern)):
                pack.load(path)
