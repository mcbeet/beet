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
from dataclasses import dataclass, field
from gzip import GzipFile
from typing import MutableSequence, Optional, TypeVar

from nbtlib.contrib.minecraft import StructureFile, StructureFileData

from beet.core.utils import extra_field

from .base import FileContainer, FileContainerProxyDescriptor, Namespace, Pack
from .file import (
    BinaryFileBase,
    FileValueAlias,
    JsonFile,
    TextFileBase,
    TextFileContent,
)


class Advancement(JsonFile):
    scope = ("advancements",)


@dataclass
class Function(TextFileBase[MutableSequence[str]]):
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


class LootTable(JsonFile):
    scope = ("loot_tables",)


class Predicate(JsonFile):
    scope = ("predicates",)


class Recipe(JsonFile):
    scope = ("recipes",)


class Structure(BinaryFileBase[StructureFileData]):
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


class TagFile(JsonFile):
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


class DimensionType(JsonFile):
    scope = ("dimension_type",)


class Dimension(JsonFile):
    scope = ("dimension",)


class Biome(JsonFile):
    scope = ("worldgen", "biome")


class ConfiguredCarver(JsonFile):
    scope = ("worldgen", "configured_carver")


class ConfiguredFeature(JsonFile):
    scope = ("worldgen", "configured_feature")


class ConfiguredStructureFeature(JsonFile):
    scope = ("worldgen", "configured_structure_feature")


class ConfiguredSurfaceBuilder(JsonFile):
    scope = ("worldgen", "configured_surface_builder")


class NoiseSettings(JsonFile):
    scope = ("worldgen", "noise_settings")


class ProcessorList(JsonFile):
    scope = ("worldgen", "processor_list")


class TemplatePool(JsonFile):
    scope = ("worldgen", "template_pool")


@dataclass(repr=False)
class DataPackNamespace(Namespace):
    # fmt: off
    advancements                 : FileContainer[Advancement]                = field(default_factory=FileContainer)
    functions                    : FileContainer[Function]                   = field(default_factory=FileContainer)
    loot_tables                  : FileContainer[LootTable]                  = field(default_factory=FileContainer)
    predicates                   : FileContainer[Predicate]                  = field(default_factory=FileContainer)
    recipes                      : FileContainer[Recipe]                     = field(default_factory=FileContainer)
    structures                   : FileContainer[Structure]                  = field(default_factory=FileContainer)
    block_tags                   : FileContainer[BlockTag]                   = field(default_factory=FileContainer)
    entity_type_tags             : FileContainer[EntityTypeTag]              = field(default_factory=FileContainer)
    fluid_tags                   : FileContainer[FluidTag]                   = field(default_factory=FileContainer)
    function_tags                : FileContainer[FunctionTag]                = field(default_factory=FileContainer)
    item_tags                    : FileContainer[ItemTag]                    = field(default_factory=FileContainer)
    dimension_types              : FileContainer[DimensionType]              = field(default_factory=FileContainer)
    dimensions                   : FileContainer[Dimension]                  = field(default_factory=FileContainer)
    biomes                       : FileContainer[Biome]                      = field(default_factory=FileContainer)
    configured_carvers           : FileContainer[ConfiguredCarver]           = field(default_factory=FileContainer)
    configured_features          : FileContainer[ConfiguredFeature]          = field(default_factory=FileContainer)
    configured_structure_features: FileContainer[ConfiguredStructureFeature] = field(default_factory=FileContainer)
    configured_surface_builders  : FileContainer[ConfiguredSurfaceBuilder]   = field(default_factory=FileContainer)
    noise_settings               : FileContainer[NoiseSettings]              = field(default_factory=FileContainer)
    processor_lists              : FileContainer[ProcessorList]              = field(default_factory=FileContainer)
    template_pools               : FileContainer[TemplatePool]               = field(default_factory=FileContainer)
    # fmt: on

    directory = "data"


class DataPack(Pack[DataPackNamespace]):
    # fmt: off
    advancements                  = FileContainerProxyDescriptor(Advancement)
    functions                     = FileContainerProxyDescriptor(Function)
    loot_tables                   = FileContainerProxyDescriptor(LootTable)
    predicates                    = FileContainerProxyDescriptor(Predicate)
    recipes                       = FileContainerProxyDescriptor(Recipe)
    structures                    = FileContainerProxyDescriptor(Structure)
    block_tags                    = FileContainerProxyDescriptor(BlockTag)
    entity_type_tags              = FileContainerProxyDescriptor(EntityTypeTag)
    fluid_tags                    = FileContainerProxyDescriptor(FluidTag)
    function_tags                 = FileContainerProxyDescriptor(FunctionTag)
    item_tags                     = FileContainerProxyDescriptor(ItemTag)
    dimension_types               = FileContainerProxyDescriptor(DimensionType)
    dimensions                    = FileContainerProxyDescriptor(Dimension)
    biomes                        = FileContainerProxyDescriptor(Biome)
    configured_carvers            = FileContainerProxyDescriptor(ConfiguredCarver)
    configured_features           = FileContainerProxyDescriptor(ConfiguredFeature)
    configured_structure_features = FileContainerProxyDescriptor(ConfiguredStructureFeature)
    configured_surface_builders   = FileContainerProxyDescriptor(ConfiguredSurfaceBuilder)
    noise_settings                = FileContainerProxyDescriptor(NoiseSettings)
    processor_lists               = FileContainerProxyDescriptor(ProcessorList)
    template_pools                = FileContainerProxyDescriptor(TemplatePool)
    # fmt: on

    default_name = "untitled_data_pack"
    latest_pack_format = 6
