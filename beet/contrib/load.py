"""Plugin that loads data packs and resource packs."""


__all__ = [
    "LoadOptions",
    "load",
]


from glob import glob
from pathlib import Path
from zipfile import ZipFile

from beet import Context, ErrorMessage, PackLoadOptions, PluginOptions, configurable


class LoadOptions(PluginOptions):
    resource_pack: PackLoadOptions = PackLoadOptions()
    data_pack: PackLoadOptions = PackLoadOptions()


def beet_default(ctx: Context):
    ctx.require(load)


@configurable(validator=LoadOptions)
def load(ctx: Context, opts: LoadOptions):
    """Plugin that loads data packs and resource packs."""
    for load_options, pack in zip([opts.resource_pack, opts.data_pack], ctx.packs):
        for load_entry in load_options.entries():
            if isinstance(load_entry, dict):
                for prefix, mount_options in load_entry.items():
                    entries = [
                        Path(entry)
                        for pattern in mount_options.entries()
                        for entry in glob(str(ctx.directory / pattern))
                    ]
                    if not entries:
                        raise ErrorMessage(f'Couldn\'t mount "{prefix}".')
                    for entry in entries:
                        dst = f"{prefix}/{entry.name}" if len(entries) > 1 else prefix
                        if entry.is_file() and entry.suffix == ".zip":
                            entry = ZipFile(entry)
                        pack.mount(dst, entry)
            else:
                if paths := glob(str(ctx.directory / load_entry)):
                    for path in paths:
                        pack.load(path)
                else:
                    raise ErrorMessage(f'Couldn\'t load "{load_entry}".')
