"""
Plugin to load snapshot pack formats and command trees from misode/mcmeta (or custom).
"""

from beet import Context, DataPack, ResourcePack
from beet.resources.pack_format_registry import (
    PackFormatRegistry,
    all_versions,
    pack_format_registry,
)
from beet.toolchain.context import PluginOptions
from beet import configurable


class SnapshotOptions(PluginOptions):
    """Plugin options for the snapshot plugin."""

    url_versions: str = "https://raw.githubusercontent.com/misode/mcmeta/refs/tags/{version}-summary/version.json"
    """URL template to download the version manifest from. The {version} placeholder will be replaced with the Minecraft version."""

    url_command_tree: str = "https://raw.githubusercontent.com/misode/mcmeta/refs/tags/{version}-summary/commands/data.json"
    """URL template to download the command tree from. The {version} placeholder will be replaced with the Minecraft version."""


@configurable("snapshot", validator=SnapshotOptions)
def beet_default(ctx: Context, opts: SnapshotOptions):
    cache = ctx.cache["snapshot"]
    path = cache.download(opts.url_versions.format(version=ctx.minecraft_version))

    all_versions.append(ctx.minecraft_version)

    pack_format = PackFormatRegistry.model_validate_json(path.open("r").read())
    pack_format_registry.append(pack_format)
    for pack in ctx.packs:
        pack.pack_format_registry.add_format(pack_format)
        pack.assign_format(ctx.minecraft_version)
    DataPack.pack_format_registry.add_format(pack_format)
    ResourcePack.pack_format_registry.add_format(pack_format)

    path = cache.download(opts.url_command_tree.format(version=ctx.minecraft_version))
    ctx.meta.setdefault("mecha", {}).setdefault("commands", []).insert(0, path)
