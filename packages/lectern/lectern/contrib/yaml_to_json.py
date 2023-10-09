"""Plugin that handles yaml fragments for json files."""


__all__ = [
    "handle_yaml",
]


from dataclasses import replace
from typing import Mapping

import yaml
from beet import Context, JsonFile

from lectern import (
    DataPackDirective,
    Directive,
    Document,
    Fragment,
    NamespacedResourceDirective,
    ResourcePackDirective,
)


def beet_default(ctx: Context):
    document = ctx.inject(Document)
    document.loaders.append(handle_yaml)


def handle_yaml(fragment: Fragment, directives: Mapping[str, Directive]) -> Fragment:
    """Loader that converts yaml to json."""
    directive = directives.get(fragment.directive)
    is_yaml = False

    if isinstance(directive, NamespacedResourceDirective):
        is_yaml = directive.file_type.extension == ".json"

    elif isinstance(directive, (DataPackDirective, ResourcePackDirective)):
        relative_path = fragment.expect("relative_path")
        if is_yaml := relative_path.endswith((".yml", ".yaml")):
            fragment = replace(
                fragment,
                arguments=[
                    relative_path.replace(".yml", ".json").replace(".yaml", ".json")
                ],
            )

    if is_yaml:
        yaml_file = fragment.as_file(JsonFile)
        yaml_file.ensure_deserialized(yaml.safe_load)
        fragment = replace(fragment, file=yaml_file)

    return fragment
