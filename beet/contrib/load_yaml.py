"""Plugin that loads yaml resources for data packs and resource packs."""


__all__ = [
    "LoadYamlOptions",
    "YamlPackLoader",
    "load_yaml",
]


import logging
from dataclasses import InitVar, dataclass, field
from typing import Any, Optional

import yaml

from beet import (
    Context,
    DataPack,
    ExtraContainer,
    FileOrigin,
    Namespace,
    Pack,
    PackFile,
    PackType,
    PluginOptions,
    ResourcePack,
    configurable,
)

logger = logging.getLogger(__name__)


class LoadYamlOptions(PluginOptions):
    resource_pack: list[str] = []
    data_pack: list[str] = []


def beet_default(ctx: Context):
    ctx.require(load_yaml)


@configurable(validator=LoadYamlOptions)
def load_yaml(ctx: Context, opts: LoadYamlOptions):
    """Plugin that loads yaml resources for data packs and resource packs."""
    yaml_pack_loader = ctx.inject(YamlPackLoader)

    for pattern in opts.resource_pack:
        for path in ctx.directory.glob(pattern):
            yaml_pack_loader.load_resource_pack(ctx.directory / path)
    for pattern in opts.data_pack:
        for path in ctx.directory.glob(pattern):
            yaml_pack_loader.load_data_pack(ctx.directory / path)


@dataclass
class YamlPackLoader:
    """Loader for data packs and resource packs using yaml files."""

    ctx: InitVar[Optional[Context]] = None

    assets: ResourcePack = field(default_factory=ResourcePack)
    data: DataPack = field(default_factory=DataPack)

    def __post_init__(self, ctx: Optional[Context]):
        logger.warning("Deprecated in favor of beet.contrib.auto_yaml.")
        if ctx:
            self.assets = ctx.assets
            self.data = ctx.data

    def load_resource_pack(self, origin: FileOrigin):
        extended_pack = self.create_extended_pack(ResourcePack)
        extended_pack.load(origin)
        self.merge_extended_pack(self.assets, extended_pack)

    def load_data_pack(self, origin: FileOrigin):
        extended_pack = self.create_extended_pack(DataPack)
        extended_pack.load(origin)
        self.merge_extended_pack(self.data, extended_pack)

    def create_extended_pack(self, pack_type: type[PackType]) -> PackType:
        # Using this variable fixes "unknown type" errors in Pyright, with or without the type annotation
        namespace_type: type[Namespace] = pack_type.namespace_type

        class ExtendedNamespace(namespace_type):
            @classmethod
            def get_extra_info(cls) -> dict[str, type[PackFile]]:
                return self.rewrite_extra_info(super().get_extra_info())

        ExtendedNamespace.field_map = namespace_type.field_map
        ExtendedNamespace.scope_map = {
            (scope, yaml_extension): key
            for yaml_extension in [".yml", ".yaml"]
            for (scope, extension), key in namespace_type.scope_map.items()
            if extension == ".json"
        }

        # Using this variable fixes "unknown type" errors in Pyright
        pack_base: type[Pack[Any]] = pack_type

        class ExtendedPack(pack_base):
            @classmethod
            def get_extra_info(cls) -> dict[str, type[PackFile]]:
                return self.rewrite_extra_info(super().get_extra_info())

        ExtendedPack.namespace_type = ExtendedNamespace

        return ExtendedPack()  # type: ignore

    def rewrite_extra_info(
        self,
        original: dict[str, type[PackFile]],
    ) -> dict[str, type[PackFile]]:
        return {
            filename[:-5] + yaml_extension: file_type
            for yaml_extension in [".yml", ".yaml"]
            for filename, file_type in original.items()
            if filename.endswith(".json")
        }

    def merge_extended_pack(self, destination: PackType, extended_pack: PackType):
        for _, yaml_file in extended_pack.list_files():
            yaml_file.ensure_deserialized(yaml.safe_load)

        self.rename_extra_files(extended_pack.extra)
        for namespace in extended_pack.values():
            self.rename_extra_files(namespace.extra)

        destination.merge(extended_pack)

    def rename_extra_files(self, extra: ExtraContainer):
        renamed = {
            path.replace(".yml", ".json").replace(".yaml", ".json"): item
            for path, item in extra.items()
            if path.endswith((".yml", ".yaml"))
        }
        extra.clear()
        extra.update(renamed)
