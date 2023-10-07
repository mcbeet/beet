"""Plugin that invokes the built-in template renderer."""


__all__ = [
    "RenderOptions",
    "render",
]


from typing import Any

from beet import Context, PluginOptions, TextFileBase, configurable
from beet.toolchain.select import PackMatchOption, PackSelector


class RenderOptions(PluginOptions):
    resource_pack: PackMatchOption = PackMatchOption()
    data_pack: PackMatchOption = PackMatchOption()


def beet_default(ctx: Context):
    ctx.require(render)


@configurable(validator=RenderOptions)
def render(ctx: Context, opts: RenderOptions):
    """Plugin that processes the data pack and the resource pack with Jinja."""
    for groups, pack in zip([opts.resource_pack, opts.data_pack], ctx.packs):
        for file_instance, (_, path) in (
            PackSelector.from_options(groups, template=ctx.template)
            .select_files(pack, extend=TextFileBase[Any])
            .items()
        ):
            with ctx.override(
                render_path=path,
                render_group=f"{file_instance.snake_name}s",
            ):
                ctx.template.render_file(file_instance)
