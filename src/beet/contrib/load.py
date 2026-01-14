"""Plugin that loads data packs and resource packs."""

__all__ = [
    "LoadOptions",
    "load",
    "evaluate_pattern",
]


from glob import glob
from pathlib import Path
from typing import List
from zipfile import ZipFile

from beet import (
    Cache,
    Context,
    ErrorMessage,
    PackageablePath,
    PackLoadOptions,
    PluginOptions,
    configurable,
)


class LoadOptions(PluginOptions):
    resource_pack: PackLoadOptions = PackLoadOptions()
    data_pack: PackLoadOptions = PackLoadOptions()


def beet_default(ctx: Context):
    ctx.require(load)


@configurable(validator=LoadOptions)
def load(ctx: Context, opts: LoadOptions):
    """Plugin that loads data packs and resource packs."""
    cache = ctx.cache["load"]
    for load_options, pack in zip([opts.resource_pack, opts.data_pack], ctx.packs):
        for load_entry in load_options.entries():
            if isinstance(load_entry, dict):
                for prefix, mount_options in load_entry.items():
                    entries = [
                        entry
                        for pattern in mount_options.entries()
                        for entry in evaluate_pattern(cache, ctx.directory, pattern)
                    ]
                    if not entries:
                        raise ErrorMessage(f'Couldn\'t mount "{prefix}".')
                    for entry in entries:
                        dst = f"{prefix}/{entry.name}" if len(entries) > 1 else prefix
                        if entry.is_file() and entry.suffix == ".zip":
                            entry = ZipFile(entry)
                        pack.mount(dst, entry)
            else:
                if paths := evaluate_pattern(cache, ctx.directory, load_entry):
                    for path in paths:
                        pack.load(path)
                else:
                    raise ErrorMessage(f'Couldn\'t load "{load_entry}".')


def evaluate_pattern(
    cache: Cache,
    directory: Path,
    pattern: PackageablePath,
) -> List[Path]:
    if url := pattern.http_url:
        return [cache.download(url)]
    else:
        return [Path(entry) for entry in sorted(glob(str(directory / pattern)))]
