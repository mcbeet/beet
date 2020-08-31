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

from .common import Pack, Namespace, FileContainer, File, JsonFile, dump_data
from .utils import FileSystemPath


@dataclass
class Advancement(JsonFile):
    PATH = ["advancements"]


@dataclass
class Function(File):
    lines: Optional[List[str]] = None

    PATH = ["functions"]
    EXTENSION = ".mcfunction"

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
    advancements: FileContainer[Advancement] = FileContainer[Advancement].field()
    functions: FileContainer[Function] = FileContainer[Function].field()
    loot_tables: FileContainer[LootTable] = FileContainer[LootTable].field()
    predicates: FileContainer[Predicate] = FileContainer[Predicate].field()
    recipes: FileContainer[Recipe] = FileContainer[Recipe].field()
    structures: FileContainer[Structure] = FileContainer[Structure].field()
    block_tags: FileContainer[BlockTag] = FileContainer[BlockTag].field()
    entity_type_tags: FileContainer[EntityTypeTag] = FileContainer[EntityTypeTag].field()
    fluid_tags: FileContainer[FluidTag] = FileContainer[FluidTag].field()
    function_tags: FileContainer[FunctionTag] = FileContainer[FunctionTag].field()
    item_tags: FileContainer[ItemTag] = FileContainer[ItemTag].field()
    dimension_types: FileContainer[DimensionType] = FileContainer[DimensionType].field()
    dimensions: FileContainer[Dimension] = FileContainer[Dimension].field()
    biomes: FileContainer[Biome] = FileContainer[Biome].field()
    configured_carvers: FileContainer[ConfiguredCarver] = FileContainer[ConfiguredCarver].field()
    configured_features: FileContainer[ConfiguredFeature] = FileContainer[ConfiguredFeature].field()
    configured_structure_features: FileContainer[ConfiguredStructureFeature] = FileContainer[ConfiguredStructureFeature].field()
    configured_surface_builders: FileContainer[ConfiguredSurfaceBuilder] = FileContainer[ConfiguredSurfaceBuilder].field()
    noise_settings: FileContainer[NoiseSettings] = FileContainer[NoiseSettings].field()
    processor_lists: FileContainer[ProcessorList] = FileContainer[ProcessorList].field()
    template_pools: FileContainer[TemplatePool] = FileContainer[TemplatePool].field()
    # fmt: on

    DIRECTORY = "data"


@dataclass
class DataPack(Pack[DataPackNamespace]):
    LATEST_PACK_FORMAT = 6
