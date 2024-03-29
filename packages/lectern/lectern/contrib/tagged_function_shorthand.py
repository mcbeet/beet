__all__ = [
    "tagged_function_shorthand",
    "TaggedFunctionDirective",
]


from dataclasses import dataclass, replace
from typing import Dict, Sequence, Type

from beet import (
    Context,
    DataPack,
    Function,
    Generator,
    ListOption,
    NamespaceFile,
    PluginOptions,
    ResourcePack,
    configurable,
)
from beet.core.utils import required_field

from lectern import Document, Fragment, NamespacedResourceDirective


class TaggedFunctionOptions(PluginOptions):
    tags: Dict[str, ListOption[str]] = {}


def beet_default(ctx: Context):
    ctx.require(tagged_function_shorthand)


@configurable(validator=TaggedFunctionOptions)
def tagged_function_shorthand(ctx: Context, opts: TaggedFunctionOptions):
    document = ctx.inject(Document)
    for shorthand, tags in opts.tags.items():
        document.directives[f"{shorthand}_function"] = TaggedFunctionDirective(
            shorthand=shorthand,
            tags=tags.entries(),
            generate=ctx.generate,
        )


@dataclass
class TaggedFunctionDirective(NamespacedResourceDirective):
    shorthand: str = required_field()
    tags: Sequence[str] = required_field()
    generate: Generator = required_field()

    file_type: Type[NamespaceFile] = Function

    def __call__(self, fragment: Fragment, assets: ResourcePack, data: DataPack):
        if not fragment.arguments:
            fragment = replace(
                fragment, arguments=(self.generate.path(self.shorthand),)
            )

        super().__call__(fragment, assets, data)

        full_name = fragment.expect("full_name")

        for tag in self.tags:
            data.function_tags.setdefault(tag).add(full_name)
