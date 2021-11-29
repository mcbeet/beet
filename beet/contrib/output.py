"""Plugin that outputs the data pack and the resource pack in a local directory."""


__all__ = [
    "OutputOptions",
    "output",
]


from typing import List, Optional, Union

from pydantic import BaseModel

from beet import Context, configurable
from beet.core.utils import FileSystemPath, log_time


class OutputOptions(BaseModel):
    directory: Optional[Union[FileSystemPath, List[FileSystemPath]]] = None


def beet_default(ctx: Context):
    ctx.require(output)


@configurable(validator=OutputOptions)
def output(ctx: Context, opts: OutputOptions):
    """Plugin that outputs the data pack and the resource pack in a local directory."""
    if not opts.directory:
        return

    paths = opts.directory if isinstance(opts.directory, list) else [opts.directory]
    paths = [ctx.directory / path for path in paths]

    packs = list(filter(None, ctx.packs))

    if paths and packs:
        with log_time("Output files."):
            for pack in packs:
                for path in paths:
                    pack.save(path, overwrite=True)
