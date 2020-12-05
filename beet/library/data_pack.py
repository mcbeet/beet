__all__ = [
    "DataPack",
    "DataPackNamespace",
    "Advancement",
    "Function",
    "LootTable",
    "Predicate",
    "Recipe",
    "Structure",
    "TagFile",
    "BlockTag",
    "EntityTypeTag",
    "FluidTag",
    "FunctionTag",
    "ItemTag",
    "DimensionType",
    "Dimension",
    "Biome",
    "ConfiguredCarver",
    "ConfiguredFeature",
    "ConfiguredStructureFeature",
    "ConfiguredSurfaceBuilder",
    "NoiseSettings",
    "ProcessorList",
    "TemplatePool",
]


import io
from copy import deepcopy
from dataclasses import dataclass
from gzip import GzipFile
from typing import MutableSequence, Optional, TypeVar

from nbtlib.contrib.minecraft import StructureFile, StructureFileData

from beet.core.file import (
    BinaryFileBase,
    BinaryFileContent,
    FileValueAlias,
    TextFileBase,
    TextFileContent,
)
from beet.core.utils import extra_field

from .base import (
    Namespace,
    NamespaceFile,
    NamespaceJsonFile,
    NamespacePin,
    NamespaceProxyDescriptor,
    Pack,
)


class Advancement(NamespaceJsonFile):
    scope = ("advancements",)


@dataclass
class Function(TextFileBase[MutableSequence[str]], NamespaceFile):
    content: TextFileContent[MutableSequence[str]] = None
    tags: Optional[MutableSequence[str]] = extra_field(default=None)

    scope = ("functions",)
    extension = ".mcfunction"

    lines = FileValueAlias[MutableSequence[str]]()

    @classmethod
    def to_str(cls, content: MutableSequence[str]) -> str:
        return "\n".join(content) + "\n"

    @classmethod
    def from_str(cls, content: str) -> MutableSequence[str]:
        return content.splitlines()

    def bind(self, pack: "DataPack", namespace: str, path: str):
        for tag_name in self.tags or ():
            pack.function_tags.merge(
                {tag_name: FunctionTag({"values": [f"{namespace}:{path}"]})}
            )


class LootTable(NamespaceJsonFile):
    scope = ("loot_tables",)


class Predicate(NamespaceJsonFile):
    scope = ("predicates",)


class Recipe(NamespaceJsonFile):
    scope = ("recipes",)


class Structure(BinaryFileBase[StructureFileData], NamespaceFile):
    content: BinaryFileContent[StructureFileData] = None
    scope = ("structures",)
    extension = ".nbt"

    data = FileValueAlias[StructureFileData]()

    @classmethod
    def from_bytes(cls, content: bytes) -> StructureFileData:
        with GzipFile(fileobj=io.BytesIO(content)) as fileobj:
            return StructureFile.parse(fileobj).root

    @classmethod
    def to_bytes(cls, content: StructureFileData) -> bytes:
        dst = io.BytesIO()
        with GzipFile(fileobj=dst, mode="wb") as fileobj:
            StructureFile(content).write(fileobj)
        return dst.getvalue()


TagFileType = TypeVar("TagFileType", bound="TagFile")


class TagFile(NamespaceJsonFile):
    def merge(self: TagFileType, other: TagFileType) -> bool:
        if other.data.get("replace"):
            self.data["replace"] = True

        values = self.data.setdefault("values", [])

        for value in other.data.get("values", []):
            if value not in values:
                values.append(deepcopy(value))
        return True


class BlockTag(TagFile):
    scope = ("tags", "blocks")


class EntityTypeTag(TagFile):
    scope = ("tags", "entity_types")


class FluidTag(TagFile):
    scope = ("tags", "fluids")


class FunctionTag(TagFile):
    scope = ("tags", "functions")


class ItemTag(TagFile):
    scope = ("tags", "items")


class DimensionType(NamespaceJsonFile):
    scope = ("dimension_type",)


class Dimension(NamespaceJsonFile):
    scope = ("dimension",)


class Biome(NamespaceJsonFile):
    scope = ("worldgen", "biome")


class ConfiguredCarver(NamespaceJsonFile):
    scope = ("worldgen", "configured_carver")


class ConfiguredFeature(NamespaceJsonFile):
    scope = ("worldgen", "configured_feature")


class ConfiguredStructureFeature(NamespaceJsonFile):
    scope = ("worldgen", "configured_structure_feature")


class ConfiguredSurfaceBuilder(NamespaceJsonFile):
    scope = ("worldgen", "configured_surface_builder")


class NoiseSettings(NamespaceJsonFile):
    scope = ("worldgen", "noise_settings")


class ProcessorList(NamespaceJsonFile):
    scope = ("worldgen", "processor_list")


class TemplatePool(NamespaceJsonFile):
    scope = ("worldgen", "template_pool")


class DataPackNamespace(Namespace):
    # fmt: off
    advancements                  = NamespacePin(Advancement)
    functions                     = NamespacePin(Function)
    loot_tables                   = NamespacePin(LootTable)
    predicates                    = NamespacePin(Predicate)
    recipes                       = NamespacePin(Recipe)
    structures                    = NamespacePin(Structure)
    block_tags                    = NamespacePin(BlockTag)
    entity_type_tags              = NamespacePin(EntityTypeTag)
    fluid_tags                    = NamespacePin(FluidTag)
    function_tags                 = NamespacePin(FunctionTag)
    item_tags                     = NamespacePin(ItemTag)
    dimension_types               = NamespacePin(DimensionType)
    dimensions                    = NamespacePin(Dimension)
    biomes                        = NamespacePin(Biome)
    configured_carvers            = NamespacePin(ConfiguredCarver)
    configured_features           = NamespacePin(ConfiguredFeature)
    configured_structure_features = NamespacePin(ConfiguredStructureFeature)
    configured_surface_builders   = NamespacePin(ConfiguredSurfaceBuilder)
    noise_settings                = NamespacePin(NoiseSettings)
    processor_lists               = NamespacePin(ProcessorList)
    template_pools                = NamespacePin(TemplatePool)
    # fmt: on

    directory = "data"


class DataPack(Pack[DataPackNamespace]):
    # fmt: off
    advancements                  = NamespaceProxyDescriptor(Advancement)
    functions                     = NamespaceProxyDescriptor(Function)
    loot_tables                   = NamespaceProxyDescriptor(LootTable)
    predicates                    = NamespaceProxyDescriptor(Predicate)
    recipes                       = NamespaceProxyDescriptor(Recipe)
    structures                    = NamespaceProxyDescriptor(Structure)
    block_tags                    = NamespaceProxyDescriptor(BlockTag)
    entity_type_tags              = NamespaceProxyDescriptor(EntityTypeTag)
    fluid_tags                    = NamespaceProxyDescriptor(FluidTag)
    function_tags                 = NamespaceProxyDescriptor(FunctionTag)
    item_tags                     = NamespaceProxyDescriptor(ItemTag)
    dimension_types               = NamespaceProxyDescriptor(DimensionType)
    dimensions                    = NamespaceProxyDescriptor(Dimension)
    biomes                        = NamespaceProxyDescriptor(Biome)
    configured_carvers            = NamespaceProxyDescriptor(ConfiguredCarver)
    configured_features           = NamespaceProxyDescriptor(ConfiguredFeature)
    configured_structure_features = NamespaceProxyDescriptor(ConfiguredStructureFeature)
    configured_surface_builders   = NamespaceProxyDescriptor(ConfiguredSurfaceBuilder)
    noise_settings                = NamespaceProxyDescriptor(NoiseSettings)
    processor_lists               = NamespaceProxyDescriptor(ProcessorList)
    template_pools                = NamespaceProxyDescriptor(TemplatePool)
    # fmt: on

    default_name = "untitled_data_pack"
    latest_pack_format = 6
