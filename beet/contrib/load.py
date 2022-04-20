"""Plugin that loads data packs and resource packs."""


__all__ = [
    "LoadOptions",
    "LoadError",
    "load",
]


from glob import glob
from pathlib import Path
from typing import List, Tuple, Union

from pydantic import BaseModel

from beet import Context, Pipeline, configurable
from beet.core.utils import import_from_string
from beet.toolchain.pipeline import FormattedPipelineException


class LoadError(FormattedPipelineException):
    """Raised when loading data packs or resource packs fails."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
        self.format_cause = True


class LoadOptions(BaseModel):
    resource_pack: Union[str, List[Union[str, Tuple[str, str]]]] = []
    data_pack: Union[str, List[Union[str, Tuple[str, str]]]] = []


def beet_default(ctx: Context):
    ctx.require(load)


@configurable(validator=LoadOptions)
def load(ctx: Context, opts: LoadOptions):
    """Plugin that loads data packs and resource packs."""
    whitelist = ctx.inject(Pipeline).whitelist

    for config, pack in zip([opts.resource_pack, opts.data_pack], ctx.packs):
        for target in [config] if isinstance(config, str) else config:
            if isinstance(target, tuple):
                package_name, target = target

                try:
                    package = import_from_string(package_name, whitelist=whitelist)
                except Exception as exc:
                    msg = f'Couldn\'t import package "{package_name}" for loading "{target}".'
                    raise LoadError(msg) from exc

                if filename := getattr(package, "__file__", None):
                    pattern = Path(filename).parent / target
                else:
                    msg = f'Missing "__file__" attribute on package "{package_name}" for loading "{target}".'
                    raise LoadError(msg)

            else:
                package_name = None
                pattern = ctx.directory / target

            if paths := glob(str(pattern)):
                for path in paths:
                    pack.load(path)
            elif package_name:
                msg = f'Couldn\'t load "{target}" from package "{package_name}".'
                raise LoadError(msg)
            else:
                msg = f'Couldn\'t load "{pattern}".'
                raise LoadError(msg)
