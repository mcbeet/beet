"""Plugin that handles relative resource locations."""


__all__ = [
    "RelativeNamespacedResourceDirective",
]


from dataclasses import dataclass, replace

from beet import Context, DataPack, ResourcePack

from lectern import Document, Fragment, NamespacedResourceDirective


def beet_default(ctx: Context):
    document = ctx.inject(Document)
    document.directives.update(
        (name, RelativeNamespacedResourceDirective(directive.file_type, ctx))
        for name, directive in document.directives.items()
        if isinstance(directive, NamespacedResourceDirective)
    )


@dataclass
class RelativeNamespacedResourceDirective(NamespacedResourceDirective):
    """Directive that handles relative resource locations."""

    ctx: Context

    def __call__(self, fragment: Fragment, assets: ResourcePack, data: DataPack):
        name = fragment.expect("name")

        if ":" not in name:
            fragment = replace(fragment, arguments=[self.ctx.generate.path(name)])

        super().__call__(fragment, assets, data)
