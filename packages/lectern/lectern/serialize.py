__all__ = [
    "TextSerializer",
    "MarkdownSerializer",
    "NAMESPACED_RESOURCE_DIRECTIVES",
]

from itertools import chain
from typing import Any, Dict, Tuple

from beet import DataPack, File, ResourcePack

from .directive import NamespacedResourceDirective, get_builtin_directives

NAMESPACED_RESOURCE_DIRECTIVES = {
    directive.file_type: directive_name
    for directive_name, directive in get_builtin_directives().items()
    if isinstance(directive, NamespacedResourceDirective)
}


class TextSerializer:
    """Document serializer that outputs plain text."""

    def serialize(self, assets: ResourcePack, data: DataPack) -> str:
        """Return the serialized representation."""
        return "\n".join(
            f"@{directive_name} {argument}\n{content}"
            for pack, extra_directive in [
                (assets, "resource_pack"),
                (data, "data_pack"),
            ]
            if pack
            for directive_name, argument, file_instance in chain(
                (
                    (extra_directive, path, file_instance)
                    for path, file_instance in pack.extra.items()
                ),
                (
                    (
                        NAMESPACED_RESOURCE_DIRECTIVES[file_type],
                        f"{name}:{path}",
                        file_instance,
                    )
                    for name, namespace in pack.items()
                    for file_type, container in namespace.items()
                    for path, file_instance in container.items()
                ),
            )
            if isinstance(content := file_instance.ensure_serialized(), str)
        )


class MarkdownSerializer:
    """Document serializer that outputs markdown and emits associated files."""

    def serialize_and_emit_files(
        self,
        assets: ResourcePack,
        data: DataPack,
    ) -> Tuple[str, Dict[str, File[Any, Any]]]:
        """Return the serialized representation and the files emitted in the process."""
        return "", {}
