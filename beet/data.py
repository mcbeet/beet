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


import io
from dataclasses import dataclass, field
from gzip import GzipFile
from typing import List, Optional, Union

from nbtlib.contrib.minecraft import StructureFile, StructureFileData

from .common import (
    Pack,
    Namespace,
    FileContainer,
    FileContainerProxyDescriptor,
    File,
    JsonFile,
)
from .utils import extra_field


@dataclass
class Advancement(JsonFile):
    path = ("advancements",)


@dataclass
class Function(File[List[str]]):
    raw: Optional[Union[List[str], bytes]] = None

    tags: Optional[List[str]] = extra_field(default=None)

    path = ("functions",)
    extension = ".mcfunction"

    def to_content(self, raw: bytes) -> List[str]:
        return raw.decode().splitlines()

    def to_bytes(self, content: List[str]) -> bytes:
        return ("\n".join(content) + "\n").encode()

    def bind(self, namespace: "DataPackNamespace", path: str):
        pack = namespace.pack
        assert pack
        for tag_name in self.tags or ():
            empty_tag = FunctionTag({"values": []})
            tag = pack.function_tags.setdefault(tag_name, empty_tag)
            tag.content.setdefault("values", []).append(f"{namespace.name}:{path}")


@dataclass
class LootTable(JsonFile):
    path = ("loot_tables",)


@dataclass
class Predicate(JsonFile):
    path = ("predicates",)


@dataclass
class Recipe(JsonFile):
    path = ("recipes",)


@dataclass
class Structure(File[StructureFileData]):
    raw: Optional[Union[dict, bytes]] = None

    path = ("structures",)
    extension = ".nbt"

    def to_content(self, raw: bytes) -> StructureFileData:
        with GzipFile(fileobj=io.BytesIO(raw)) as fileobj:
            return StructureFile.parse(fileobj).root

    def to_bytes(self, content: StructureFileData) -> bytes:
        dst = io.BytesIO()
        with GzipFile(fileobj=dst, mode="wb") as fileobj:
            StructureFile(content).write(fileobj)
        return dst.getvalue()


@dataclass
class BlockTag(JsonFile):
    path = ("tags", "blocks")


@dataclass
class EntityTypeTag(JsonFile):
    path = ("tags", "entity_types")


@dataclass
class FluidTag(JsonFile):
    path = ("tags", "fluids")


@dataclass
class FunctionTag(JsonFile):
    path = ("tags", "functions")


@dataclass
class ItemTag(JsonFile):
    path = ("tags", "items")


@dataclass
class DimensionType(JsonFile):
    path = ("dimension_type",)


@dataclass
class Dimension(JsonFile):
    path = ("dimension",)


@dataclass
class Biome(JsonFile):
    path = ("worldgen", "biome")


@dataclass
class ConfiguredCarver(JsonFile):
    path = ("worldgen", "configured_carver")


@dataclass
class ConfiguredFeature(JsonFile):
    path = ("worldgen", "configured_feature")


@dataclass
class ConfiguredStructureFeature(JsonFile):
    path = ("worldgen", "configured_structure_feature")


@dataclass
class ConfiguredSurfaceBuilder(JsonFile):
    path = ("worldgen", "configured_surface_builder")


@dataclass
class NoiseSettings(JsonFile):
    path = ("worldgen", "noise_settings")


@dataclass
class ProcessorList(JsonFile):
    path = ("worldgen", "processor_list")


@dataclass
class TemplatePool(JsonFile):
    path = ("worldgen", "template_pool")


@dataclass
class DataPackNamespace(Namespace):
    # fmt: off
    advancements: FileContainer[Advancement] = field(default_factory=FileContainer)
    functions: FileContainer[Function] = field(default_factory=FileContainer)
    loot_tables: FileContainer[LootTable] = field(default_factory=FileContainer)
    predicates: FileContainer[Predicate] = field(default_factory=FileContainer)
    recipes: FileContainer[Recipe] = field(default_factory=FileContainer)
    structures: FileContainer[Structure] = field(default_factory=FileContainer)
    block_tags: FileContainer[BlockTag] = field(default_factory=FileContainer)
    entity_type_tags: FileContainer[EntityTypeTag] = field(default_factory=FileContainer)
    fluid_tags: FileContainer[FluidTag] = field(default_factory=FileContainer)
    function_tags: FileContainer[FunctionTag] = field(default_factory=FileContainer)
    item_tags: FileContainer[ItemTag] = field(default_factory=FileContainer)
    dimension_types: FileContainer[DimensionType] = field(default_factory=FileContainer)
    dimensions: FileContainer[Dimension] = field(default_factory=FileContainer)
    biomes: FileContainer[Biome] = field(default_factory=FileContainer)
    configured_carvers: FileContainer[ConfiguredCarver] = field(default_factory=FileContainer)
    configured_features: FileContainer[ConfiguredFeature] = field(default_factory=FileContainer)
    configured_structure_features: FileContainer[ConfiguredStructureFeature] = field(default_factory=FileContainer)
    configured_surface_builders: FileContainer[ConfiguredSurfaceBuilder] = field(default_factory=FileContainer)
    noise_settings: FileContainer[NoiseSettings] = field(default_factory=FileContainer)
    processor_lists: FileContainer[ProcessorList] = field(default_factory=FileContainer)
    template_pools: FileContainer[TemplatePool] = field(default_factory=FileContainer)
    # fmt: on

    directory = "data"


@dataclass
class DataPack(Pack[DataPackNamespace]):
    # fmt: off
    advancements = FileContainerProxyDescriptor[Advancement]()
    functions = FileContainerProxyDescriptor[Function]()
    loot_tables = FileContainerProxyDescriptor[LootTable]()
    predicates = FileContainerProxyDescriptor[Predicate]()
    recipes = FileContainerProxyDescriptor[Recipe]()
    structures = FileContainerProxyDescriptor[Structure]()
    block_tags = FileContainerProxyDescriptor[BlockTag]()
    entity_type_tags = FileContainerProxyDescriptor[EntityTypeTag]()
    fluid_tags = FileContainerProxyDescriptor[FluidTag]()
    function_tags = FileContainerProxyDescriptor[FunctionTag]()
    item_tags = FileContainerProxyDescriptor[ItemTag]()
    dimension_types = FileContainerProxyDescriptor[DimensionType]()
    dimensions = FileContainerProxyDescriptor[Dimension]()
    biomes = FileContainerProxyDescriptor[Biome]()
    configured_carvers = FileContainerProxyDescriptor[ConfiguredCarver]()
    configured_features = FileContainerProxyDescriptor[ConfiguredFeature]()
    configured_structure_features = FileContainerProxyDescriptor[ConfiguredStructureFeature]()
    configured_surface_builders = FileContainerProxyDescriptor[ConfiguredSurfaceBuilder]()
    noise_settings = FileContainerProxyDescriptor[NoiseSettings]()
    processor_lists = FileContainerProxyDescriptor[ProcessorList]()
    template_pools = FileContainerProxyDescriptor[TemplatePool]()
    # fmt: on

    latest_pack_format = 6
