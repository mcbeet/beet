"""Plugin that loads data packs and resource packs."""


__all__ = [
    "LoadOptions",
    "LoadError",
    "load",
]


from glob import glob
from pathlib import Path

from pydantic import BaseModel

from beet import Context, LoadEntries, Pipeline, configurable
from beet.core.utils import import_from_string
from beet.toolchain.pipeline import FormattedPipelineException


class LoadError(FormattedPipelineException):
    """Raised when loading data packs or resource packs fails."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
        self.format_cause = True


class LoadOptions(BaseModel):
    resource_pack: LoadEntries = []
    data_pack: LoadEntries = []


def beet_default(ctx: Context):
    ctx.require(load)


@configurable(validator=LoadOptions)
def load(ctx: Context, opts: LoadOptions):
    """Plugin that loads data packs and resource packs."""
    whitelist = ctx.inject(Pipeline).whitelist

    for config, pack in zip([opts.resource_pack, opts.data_pack], ctx.packs):
        for target in [config] if isinstance(config, str) else config:
            if isinstance(target, tuple):
                try:
                    package = import_from_string(target[0], whitelist=whitelist)
                except Exception as exc:
                    msg = (
                        f'Couldn\'t import package "{target[0]}" for loading "{target[1]}".'
                        if len(target) == 2
                        else f'Couldn\'t import package "{target[0]}" for loading root-level pack.'
                    )
                    raise LoadError(msg) from exc

                if filename := getattr(package, "__file__", None):
                    pattern = Path(filename).parent
                else:
                    msg = (
                        f'Missing "__file__" attribute on package "{target[0]}" for loading "{target[1]}".'
                        if len(target) == 2
                        else f'Missing "__file__" attribute on package "{target[0]}" for loading root-level pack.'
                    )
                    raise LoadError(msg)

                if len(target) == 2:
                    pattern /= target[1]

            else:
                pattern = ctx.directory / target

            if paths := glob(str(pattern)):
                for path in paths:
                    pack.load(path)
            elif isinstance(target, tuple):
                msg = (
                    f'Couldn\'t load "{target[1]}" from package "{target[0]}".'
                    if len(target) == 2
                    else f'Couldn\'t load root-level pack from package "{target[0]}".'
                )
                raise LoadError(msg)
            else:
                msg = f'Couldn\'t load "{pattern}".'
                raise LoadError(msg)
