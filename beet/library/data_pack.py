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
from dataclasses import InitVar, dataclass, field
from gzip import GzipFile
from typing import List, Optional, TypeVar

from nbtlib.contrib.minecraft import StructureFile, StructureFileData

from beet.shared_utils import JsonDict, extra_field

from .base import File, FileContainer, FileContainerProxyDescriptor, Namespace, Pack
from .file import JsonFile


class Advancement(JsonFile[JsonDict]):
    scope = ("advancements",)


@dataclass
class Function(File[List[str]]):
    value: InitVar[Optional[List[str]]] = None
    tags: Optional[List[str]] = extra_field(default=None)

    scope = ("functions",)
    extension = ".mcfunction"

    def to_content(self, raw: bytes) -> List[str]:
        return raw.decode().splitlines()

    def to_bytes(self, content: List[str]) -> bytes:
        return ("\n".join(content) + "\n").encode()

    def bind(self, pack: "DataPack", namespace: str, path: str):
        for tag_name in self.tags or ():
            pack.function_tags.merge(
                {tag_name: FunctionTag({"values": [f"{namespace}:{path}"]})}
            )


class LootTable(JsonFile[JsonDict]):
    scope = ("loot_tables",)


class Predicate(JsonFile[JsonDict]):
    scope = ("predicates",)


class Recipe(JsonFile[JsonDict]):
    scope = ("recipes",)


class Structure(File[StructureFileData]):
    scope = ("structures",)
    extension = ".nbt"

    def to_content(self, raw: bytes) -> StructureFileData:
        with GzipFile(fileobj=io.BytesIO(raw)) as fileobj:
            return StructureFile.parse(fileobj).root

    def to_bytes(self, content: StructureFileData) -> bytes:
        dst = io.BytesIO()
        with GzipFile(fileobj=dst, mode="wb") as fileobj:
            StructureFile(content).write(fileobj)
        return dst.getvalue()


TagFileType = TypeVar("TagFileType", bound="TagFile")


class TagFile(JsonFile[JsonDict]):
    def merge(self: TagFileType, other: TagFileType) -> bool:
        if other.content.get("replace"):
            self.content["replace"] = True

        values = self.content.setdefault("values", [])

        for value in other.content.get("values", []):
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


class DimensionType(JsonFile[JsonDict]):
    scope = ("dimension_type",)


class Dimension(JsonFile[JsonDict]):
    scope = ("dimension",)


class Biome(JsonFile[JsonDict]):
    scope = ("worldgen", "biome")


class ConfiguredCarver(JsonFile[JsonDict]):
    scope = ("worldgen", "configured_carver")


class ConfiguredFeature(JsonFile[JsonDict]):
    scope = ("worldgen", "configured_feature")


class ConfiguredStructureFeature(JsonFile[JsonDict]):
    scope = ("worldgen", "configured_structure_feature")


class ConfiguredSurfaceBuilder(JsonFile[JsonDict]):
    scope = ("worldgen", "configured_surface_builder")


class NoiseSettings(JsonFile[JsonDict]):
    scope = ("worldgen", "noise_settings")


class ProcessorList(JsonFile[JsonDict]):
    scope = ("worldgen", "processor_list")


class TemplatePool(JsonFile[JsonDict]):
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
