"""Plugin that cleans up empty overlays."""

__all__ = [
    "cleanup_overlays",
    "CleanupOverlaysOptions",
]


from beet import Context, PluginOptions, configurable, ListOption


class CleanupOverlaysOptions(PluginOptions):
    resource_pack: ListOption[str] | None = None
    data_pack: ListOption[str] | None = None


def beet_default(ctx: Context):
    ctx.require(cleanup_overlays)


@configurable(validator=CleanupOverlaysOptions)
def cleanup_overlays(ctx: Context, opts: CleanupOverlaysOptions):
    """Plugin that cleans up empty overlays."""
    for pack, directories in zip(ctx.packs, (opts.resource_pack, opts.data_pack)):
        if directories is not None:
            directories = directories.entries()
        pack.overlays.cleanup(directories)
