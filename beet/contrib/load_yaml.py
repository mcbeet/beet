"""Plugin that loads yaml resources for data packs and resource packs."""


__all__ = [
    "YamlPackLoader",
    "load_yaml",
]


from dataclasses import InitVar, dataclass, field
from typing import Any, Dict, Iterable, Optional, Type, TypeVar, cast

import yaml

from beet import (
    Context,
    DataPack,
    File,
    FileOrigin,
    Pack,
    Plugin,
    ResourcePack,
    SupportsExtra,
)
from beet.core.utils import JsonDict

PackType = TypeVar("PackType", bound=Pack[Any])
PackFile = File[Any, Any]


def beet_default(ctx: Context):
    config = ctx.meta.get("load_yaml", cast(JsonDict, {}))

    resource_pack = config.get("resource_pack", ())
    data_pack = config.get("data_pack", ())

    ctx.require(load_yaml(resource_pack, data_pack))


def load_yaml(
    resource_pack: Iterable[str] = (),
    data_pack: Iterable[str] = (),
) -> Plugin:
    """Return a plugin that loads yaml resources for data packs and resource packs."""

    def plugin(ctx: Context):
        yaml_pack_loader = ctx.inject(YamlPackLoader)

        for path in resource_pack:
            yaml_pack_loader.load_resource_pack(ctx.directory / path)
        for path in data_pack:
            yaml_pack_loader.load_data_pack(ctx.directory / path)

    return plugin


@dataclass
class YamlPackLoader:
    """Loader for data packs and resource packs using yaml files."""

    ctx: InitVar[Optional[Context]] = None

    assets: ResourcePack = field(default_factory=ResourcePack)
    data: DataPack = field(default_factory=DataPack)

    def __post_init__(self, ctx: Optional[Context]):
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

    def create_extended_pack(self, pack_type: Type[PackType]) -> PackType:
        class ExtendedNamespace(pack_type.namespace_type):  # type: ignore
            @classmethod
            def get_extra_info(cls) -> Dict[str, Type[PackFile]]:
                return self.rewrite_extra_info(super().get_extra_info())  # type: ignore

        ExtendedNamespace.field_map = pack_type.namespace_type.field_map
        ExtendedNamespace.scope_map = {
            (scope, yaml_extension): key
            for yaml_extension in [".yml", ".yaml"]
            for (scope, extension), key in pack_type.namespace_type.scope_map.items()
            if extension == ".json"
        }

        class ExtendedPack(pack_type):  # type: ignore
            @classmethod
            def get_extra_info(cls) -> Dict[str, Type[PackFile]]:
                return self.rewrite_extra_info(super().get_extra_info())  # type: ignore

        ExtendedPack.namespace_type = ExtendedNamespace

        return ExtendedPack()  # type: ignore

    def rewrite_extra_info(
        self,
        original: Dict[str, Type[PackFile]],
    ) -> Dict[str, Type[PackFile]]:
        return {
            filename[:-5] + yaml_extension: file_type
            for yaml_extension in [".yml", ".yaml"]
            for filename, file_type in original.items()
            if filename.endswith(".json")
        }

    def merge_extended_pack(self, destination: PackType, extended_pack: PackType):
        for _, yaml_file in extended_pack.list_files():
            yaml_file.ensure_deserialized(yaml.safe_load)

        self.rename_extra_files(extended_pack)
        for namespace in extended_pack.values():
            self.rename_extra_files(namespace)

        destination.merge(extended_pack)

    def rename_extra_files(self, container: SupportsExtra):
        renamed = {
            path.replace(".yml", ".json").replace(".yaml", ".json"): item
            for path, item in container.extra.items()
            if path.endswith((".yml", ".yaml"))
        }
        container.extra.clear()
        container.extra.update(renamed)
