"""Plugin that invokes the built-in template renderer."""

__all__ = [
    "RenderOptions",
    "render",
]


from typing import Any

from beet import Context, PluginOptions, TextFileBase, configurable
from beet.toolchain.query import PackMatchOption


class RenderOptions(PluginOptions):
    resource_pack: PackMatchOption = PackMatchOption()
    data_pack: PackMatchOption = PackMatchOption()


def beet_default(ctx: Context):
    ctx.require(render)


@configurable(validator=RenderOptions)
def render(ctx: Context, opts: RenderOptions):
    """Plugin that processes the data pack and the resource pack with Jinja."""
    for match_option, pack in zip([opts.resource_pack, opts.data_pack], ctx.packs):
        for file_type, selection in (
            ctx.query.from_pack(pack)
            .prepare(match_option)
            .select(extend=TextFileBase[Any])
            .items()
        ):
            for path, file_instance in selection:
                with ctx.override(
                    render_path=path,
                    render_group=f"{file_type.snake_name}s",
                ):
                    ctx.template.render_file(file_instance)
