"""Plugin that adds a directive for requiring plugins dynamically."""


__all__ = [
    "RequireDirective",
]


from dataclasses import dataclass

from beet import Context, DataPack, ResourcePack

from lectern import Document, Fragment


def beet_default(ctx: Context):
    document = ctx.inject(Document)
    document.directives["require"] = RequireDirective(ctx)


@dataclass
class RequireDirective:
    """Directive that requires a given plugin."""

    ctx: Context

    def __call__(self, fragment: Fragment, assets: ResourcePack, data: DataPack):
        plugin = fragment.expect("plugin")

        self.ctx.require(plugin)
