"""Plugin that automatically translates yaml resources to json."""


__all__ = [
    "use_auto_yaml",
    "create_extra_handler",
    "create_namespace_handler",
    "create_namespace_extra_handler",
]


from typing import Any, ClassVar, Tuple, Type

from beet import Context, Drop, JsonFileBase, NamespaceFile, Pack, YamlFile


def beet_default(ctx: Context):
    use_auto_yaml(ctx.data)
    use_auto_yaml(ctx.assets)


def use_auto_yaml(pack: Pack[Any]):
    """Register handlers to automatically translate yaml files to json."""
    for (scope, extension), file_type in pack.resolve_scope_map().items():
        if extension == ".json" and issubclass(file_type, JsonFileBase):
            pack.extend_namespace += [
                create_namespace_handler(file_type, scope, ".yml"),
                create_namespace_handler(file_type, scope, ".yaml"),
            ]

    for extend, extra_info, handler_factory in [
        (
            pack.extend_extra,
            pack.resolve_extra_info(),
            create_extra_handler,
        ),
        (
            pack.extend_namespace_extra,
            pack.resolve_namespace_extra_info(),
            create_namespace_extra_handler,
        ),
    ]:
        for filename, file_type in extra_info.items():
            if filename.endswith(".json") and issubclass(file_type, JsonFileBase):
                base = filename[:-5]
                extend[f"{base}.yml"] = handler_factory(filename, file_type)
                extend[f"{base}.yaml"] = handler_factory(filename, file_type)


def create_namespace_handler(
    file_type: Type[JsonFileBase[Any]],
    namespace_scope: Tuple[str, ...],
    namespace_extension: str,
) -> Type[NamespaceFile]:
    """Create handler that turns yaml namespace files into json."""

    class AutoYamlNamespaceHandler(YamlFile):
        scope: ClassVar[Tuple[str, ...]] = namespace_scope
        extension: ClassVar[str] = namespace_extension

        model = file_type.model

        def bind(self, pack: Any, path: str):
            super().bind(pack, path)
            pack[file_type].merge({path: file_type(self.data, original=self.original)})
            raise Drop()

    return AutoYamlNamespaceHandler


def create_extra_handler(
    filename: str,
    file_type: Type[JsonFileBase[Any]],
) -> Type[YamlFile]:
    """Create handler that turns yaml extra files into json."""

    class AutoYamlExtraHandler(YamlFile):
        model = file_type.model

        def bind(self, pack: Any, path: str):
            super().bind(pack, path)
            pack.extra.merge({filename: file_type(self.data, original=self.original)})
            raise Drop()

    return AutoYamlExtraHandler


def create_namespace_extra_handler(
    filename: str,
    file_type: Type[JsonFileBase[Any]],
) -> Type[YamlFile]:
    """Create handler that turns yaml namespace extra files into json."""

    class AutoYamlExtraHandler(YamlFile):
        model = file_type.model

        def bind(self, pack: Any, path: str):
            super().bind(pack, path)
            namespace, _, path = path.partition(":")
            pack[namespace].extra.merge(
                {filename: file_type(self.data, original=self.original)}
            )
            raise Drop()

    return AutoYamlExtraHandler
