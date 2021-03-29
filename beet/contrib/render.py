"""Plugin that invokes the built-in template renderer."""


__all__ = [
    "render",
]


from typing import Dict, List, Optional, cast

from beet import Context, Plugin
from beet.core.utils import JsonDict


def beet_default(ctx: Context):
    config = ctx.meta.get("render", cast(JsonDict, {}))

    resource_pack = config.get("resource_pack")
    data_pack = config.get("data_pack")

    ctx.require(render(resource_pack, data_pack))


def render(
    resource_pack: Optional[Dict[str, List[str]]] = None,
    data_pack: Optional[Dict[str, List[str]]] = None,
) -> Plugin:
    """Return a plugin that processes the data pack and the resource pack with Jinja."""

    def plugin(ctx: Context):
        for groups, pack in zip([resource_pack or {}, data_pack or {}], ctx.packs):
            for group, patterns in groups.items():
                try:
                    proxy = getattr(pack, group)
                    file_paths = proxy.match(*patterns)
                except:
                    raise ValueError(f"Invalid render group {group!r}.") from None
                else:
                    for path in file_paths:
                        with ctx.override(render_path=path, render_group=group):
                            ctx.template.render_file(proxy[path])

    return plugin
