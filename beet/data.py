__all__ = [
    "DataPack",
    "DataPackNamespace",
    "Advancement",
    "Function",
    "LootTable",
    "Predicate",
    "Recipe",
    "Structure",
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


from dataclasses import dataclass
from typing import List, Optional
from zipfile import ZipFile

from .common import (
    Pack,
    Namespace,
    FileContainerProxy,
    FileContainer,
    File,
    JsonFile,
    dump_data,
)
from .utils import FileSystemPath


@dataclass
class Advancement(JsonFile):
    PATH = ["advancements"]


@dataclass
class Function(File):
    lines: Optional[List[str]] = None
    tags: Optional[List[str]] = None

    PATH = ["functions"]
    EXTENSION = ".mcfunction"

    def bind(self, namespace: "DataPackNamespace", path: str):
        for tag_name in self.tags or ():
            empty_tag = FunctionTag({"values": []})
            tag = namespace.pack.function_tags.setdefault(tag_name, empty_tag)
            tag.content.setdefault("values", []).append(f"{namespace.name}:{path}")

    def dump(self, path: FileSystemPath, zipfile: ZipFile = None):
        if self.lines is not None:
            dump_data(("\n".join(self.lines) + "\n").encode(), path, zipfile)
        else:
            super().dump(path, zipfile)


@dataclass
class LootTable(JsonFile):
    PATH = ["loot_tables"]


@dataclass
class Predicate(JsonFile):
    PATH = ["predicates"]


@dataclass
class Recipe(JsonFile):
    PATH = ["recipes"]


@dataclass
class Structure(File):
    PATH = ["structures"]
    EXTENSION = ".nbt"


@dataclass
class BlockTag(JsonFile):
    PATH = ["tags", "blocks"]


@dataclass
class EntityTypeTag(JsonFile):
    PATH = ["tags", "entity_types"]


@dataclass
class FluidTag(JsonFile):
    PATH = ["tags", "fluids"]


@dataclass
class FunctionTag(JsonFile):
    PATH = ["tags", "functions"]


@dataclass
class ItemTag(JsonFile):
    PATH = ["tags", "items"]


@dataclass
class DimensionType(JsonFile):
    PATH = ["dimension_type"]


@dataclass
class Dimension(JsonFile):
    PATH = ["dimension"]


@dataclass
class Biome(JsonFile):
    PATH = ["worldgen", "biome"]


@dataclass
class ConfiguredCarver(JsonFile):
    PATH = ["worldgen", "configured_carver"]


@dataclass
class ConfiguredFeature(JsonFile):
    PATH = ["worldgen", "configured_feature"]


@dataclass
class ConfiguredStructureFeature(JsonFile):
    PATH = ["worldgen", "configured_structure_feature"]


@dataclass
class ConfiguredSurfaceBuilder(JsonFile):
    PATH = ["worldgen", "configured_surface_builder"]


@dataclass
class NoiseSettings(JsonFile):
    PATH = ["worldgen", "noise_settings"]


@dataclass
class ProcessorList(JsonFile):
    PATH = ["worldgen", "processor_list"]


@dataclass
class TemplatePool(JsonFile):
    PATH = ["worldgen", "template_pool"]


@dataclass
class DataPackNamespace(Namespace):
    # fmt: off
    advancements: FileContainer[Advancement] = FileContainer.field()
    functions: FileContainer[Function] = FileContainer.field()
    loot_tables: FileContainer[LootTable] = FileContainer.field()
    predicates: FileContainer[Predicate] = FileContainer.field()
    recipes: FileContainer[Recipe] = FileContainer.field()
    structures: FileContainer[Structure] = FileContainer.field()
    block_tags: FileContainer[BlockTag] = FileContainer.field()
    entity_type_tags: FileContainer[EntityTypeTag] = FileContainer.field()
    fluid_tags: FileContainer[FluidTag] = FileContainer.field()
    function_tags: FileContainer[FunctionTag] = FileContainer.field()
    item_tags: FileContainer[ItemTag] = FileContainer.field()
    dimension_types: FileContainer[DimensionType] = FileContainer.field()
    dimensions: FileContainer[Dimension] = FileContainer.field()
    biomes: FileContainer[Biome] = FileContainer.field()
    configured_carvers: FileContainer[ConfiguredCarver] = FileContainer.field()
    configured_features: FileContainer[ConfiguredFeature] = FileContainer.field()
    configured_structure_features: FileContainer[ConfiguredStructureFeature] = FileContainer.field()
    configured_surface_builders: FileContainer[ConfiguredSurfaceBuilder] = FileContainer.field()
    noise_settings: FileContainer[NoiseSettings] = FileContainer.field()
    processor_lists: FileContainer[ProcessorList] = FileContainer.field()
    template_pools: FileContainer[TemplatePool] = FileContainer.field()
    # fmt: on

    DIRECTORY = "data"


@dataclass
class DataPack(Pack[DataPackNamespace]):
    advancements = FileContainerProxy.field(Advancement)
    functions = FileContainerProxy.field(Function)
    loot_tables = FileContainerProxy.field(LootTable)
    predicates = FileContainerProxy.field(Predicate)
    recipes = FileContainerProxy.field(Recipe)
    structures = FileContainerProxy.field(Structure)
    block_tags = FileContainerProxy.field(BlockTag)
    entity_type_tags = FileContainerProxy.field(EntityTypeTag)
    fluid_tags = FileContainerProxy.field(FluidTag)
    function_tags = FileContainerProxy.field(FunctionTag)
    item_tags = FileContainerProxy.field(ItemTag)
    dimension_types = FileContainerProxy.field(DimensionType)
    dimensions = FileContainerProxy.field(Dimension)
    biomes = FileContainerProxy.field(Biome)
    configured_carvers = FileContainerProxy.field(ConfiguredCarver)
    configured_features = FileContainerProxy.field(ConfiguredFeature)
    configured_structure_features = FileContainerProxy.field(ConfiguredStructureFeature)
    configured_surface_builders = FileContainerProxy.field(ConfiguredSurfaceBuilder)
    noise_settings = FileContainerProxy.field(NoiseSettings)
    processor_lists = FileContainerProxy.field(ProcessorList)
    template_pools = FileContainerProxy.field(TemplatePool)

    LATEST_PACK_FORMAT = 6
