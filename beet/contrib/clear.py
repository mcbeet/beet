"""Plugin for clearing the resource pack and the data pack."""


__all__ = [
    "ClearOptions",
    "clear",
]


from beet import Context, PluginOptions, configurable


class ClearOptions(PluginOptions):
    resource_pack: bool = True
    data_pack: bool = True


def beet_default(ctx: Context):
    ctx.require(clear)


@configurable(validator=ClearOptions)
def clear(ctx: Context, opts: ClearOptions):
    """Plugin for clearing the resource pack and the data pack."""
    if opts.resource_pack:
        ctx.assets.clear()
    if opts.data_pack:
        ctx.data.clear()
