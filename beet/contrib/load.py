"""Plugin that loads data packs and resource packs."""


__all__ = [
    "LoadOptions",
    "load",
]


from glob import glob

from pydantic import BaseModel

from beet import Context, ErrorMessage, ListOption, PackageablePath, configurable


class LoadOptions(BaseModel):
    resource_pack: ListOption[PackageablePath] = ListOption()
    data_pack: ListOption[PackageablePath] = ListOption()


def beet_default(ctx: Context):
    ctx.require(load)


@configurable(validator=LoadOptions)
def load(ctx: Context, opts: LoadOptions):
    """Plugin that loads data packs and resource packs."""
    for load_options, pack in zip([opts.resource_pack, opts.data_pack], ctx.packs):
        for target in load_options.entries():
            if paths := glob(str(ctx.directory / target)):
                for path in paths:
                    pack.load(path)
            else:
                raise ErrorMessage(f'Couldn\'t load "{target}".')
