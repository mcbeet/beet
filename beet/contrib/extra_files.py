"""Plugin that registers extra files to be loaded in the data pack and the resource pack."""


__all__ = [
    "ExtraFilesOptions",
    "extra_files",
]


from typing import List

from pydantic import BaseModel

from beet import Context, configurable

from .copy_files import guess_file_type


class ExtraFilesOptions(BaseModel):
    resource_pack: List[str] = []
    data_pack: List[str] = []
    resource_pack_namespace: List[str] = []
    data_pack_namespace: List[str] = []


def beet_default(ctx: Context):
    ctx.require(extra_files)


@configurable(validator=ExtraFilesOptions)
def extra_files(ctx: Context, opts: ExtraFilesOptions):
    """Plugin that registers extra files."""
    for extend, extras in [
        (ctx.assets.extend_extra, opts.resource_pack),
        (ctx.data.extend_extra, opts.data_pack),
        (ctx.assets.extend_namespace_extra, opts.resource_pack_namespace),
        (ctx.data.extend_namespace_extra, opts.data_pack_namespace),
    ]:
        for filename in extras:
            extend[filename] = guess_file_type(filename)
