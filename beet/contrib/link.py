"""Plugin for linking the generated resource pack and data pack to Minecraft."""


__all__ = [
    "LinkOptions",
    "link",
]


import logging
from typing import Optional

from pydantic import BaseModel

from beet import Context, configurable
from beet.core.utils import FileSystemPath, log_time, remove_path

logger = logging.getLogger("link")


class LinkOptions(BaseModel):
    resource_pack: Optional[FileSystemPath] = None
    data_pack: Optional[FileSystemPath] = None


def beet_default(ctx: Context):
    ctx.require(link)


@configurable(validator=LinkOptions)
def link(ctx: Context, opts: LinkOptions):
    """Plugin for linking the generated resource pack and data pack to Minecraft."""
    dirty = ctx.cache["link"].json.setdefault("dirty", [])
    remove_path(*dirty)
    dirty.clear()

    to_link = [
        (ctx.directory / directory, pack)
        for directory, pack in zip([opts.resource_pack, opts.data_pack], ctx.packs)
        if directory and pack
    ]

    if to_link:
        with log_time("Link project."):
            for directory, pack in to_link:
                try:
                    dirty.append(str(pack.save(directory)))
                except FileExistsError as exc:
                    logger.warning(str(exc))
