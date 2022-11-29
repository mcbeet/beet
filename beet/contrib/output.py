"""Plugin that outputs the data pack and the resource pack in a local directory."""


__all__ = [
    "OutputOptions",
    "output",
]


from typing import Optional

from beet import Context, ListOption, PluginOptions, configurable
from beet.core.utils import FileSystemPath, log_time


class OutputOptions(PluginOptions):
    directory: Optional[ListOption[FileSystemPath]] = None


def beet_default(ctx: Context):
    ctx.require(output)


@configurable(validator=OutputOptions)
def output(ctx: Context, opts: OutputOptions):
    """Plugin that outputs the data pack and the resource pack in a local directory."""
    if opts.directory is None:
        return

    paths = [ctx.directory / path for path in opts.directory.entries()]
    packs = list(filter(None, ctx.packs))

    if paths and packs:
        with log_time("Output files."):
            for pack in packs:
                for path in paths:
                    pack.save(path, overwrite=True)
