"""Plugin that handles relative resource locations."""


__all__ = [
    "RelativeNamespacedResourceLoader",
]


from dataclasses import dataclass, replace
from typing import Mapping

from beet import Context

from lectern import Directive, Document, Fragment, NamespacedResourceDirective


def beet_default(ctx: Context):
    document = ctx.inject(Document)
    document.loaders.append(RelativeNamespacedResourceLoader(ctx))


@dataclass
class RelativeNamespacedResourceLoader:
    """Loader that resolves relative resource locations."""

    ctx: Context

    def __call__(
        self,
        fragment: Fragment,
        directives: Mapping[str, Directive],
    ) -> Fragment:
        if isinstance(directives[fragment.directive], NamespacedResourceDirective):
            name = fragment.expect("name")
            if ":" not in name:
                fragment = replace(fragment, arguments=[self.ctx.generate.path(name)])
        return fragment
