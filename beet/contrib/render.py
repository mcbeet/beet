"""Plugin that invokes the built-in template renderer."""


__all__ = [
    "RenderOptions",
    "render",
]


from typing import Dict, List

from pydantic import BaseModel

from beet import Context, configurable
from beet.core.utils import snake_case


class RenderOptions(BaseModel):
    resource_pack: Dict[str, List[str]] = {}
    data_pack: Dict[str, List[str]] = {}


def beet_default(ctx: Context):
    ctx.require(render)


@configurable(validator=RenderOptions)
def render(ctx: Context, opts: RenderOptions):
    """Plugin that processes the data pack and the resource pack with Jinja."""
    for groups, pack in zip([opts.resource_pack, opts.data_pack], ctx.packs):
        file_types = {
            file_type for namespace in pack.values() for file_type in namespace
        }

        group_map = {
            snake_case(file_type.__name__): file_type for file_type in file_types
        }
        for singular in list(group_map):
            group_map[f"{singular}s"] = group_map[singular]

        for group, patterns in groups.items():
            try:
                file_type = group_map[group]
                proxy = pack[file_type]
                file_paths = proxy.match(*patterns)
            except:
                raise ValueError(f"Invalid render group {group!r}.") from None
            else:
                for path in file_paths:
                    with ctx.override(render_path=path, render_group=group):
                        ctx.template.render_file(proxy[path])  # type: ignore
