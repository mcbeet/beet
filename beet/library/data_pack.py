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
    FileDeserialize,
    JsonFile,
    TextFileBase,
    TextFileContent,
)
from beet.core.utils import extra_field

from .base import Namespace, NamespaceFile, NamespacePin, NamespaceProxyDescriptor, Pack

TagFileType = TypeVar("TagFileType", bound="TagFile")


class Advancement(JsonFile, NamespaceFile):
    """Class representing a data pack advancement."""

    scope = ("advancements",)
    extension = ".json"


@dataclass(eq=False)
class Function(TextFileBase[MutableSequence[str]], NamespaceFile):
    """Class representing a data pack function."""

    content: TextFileContent[MutableSequence[str]] = None
    tags: Optional[MutableSequence[str]] = extra_field(default=None)

    scope = ("functions",)
    extension = ".mcfunction"

    lines = FileDeserialize[MutableSequence[str]]()

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


class LootTable(JsonFile, NamespaceFile):
    """Class representing a data pack loot table."""

    scope = ("loot_tables",)
    extension = ".json"


class Predicate(JsonFile, NamespaceFile):
    """Class representing a data pack predicate."""

    scope = ("predicates",)
    extension = ".json"


class Recipe(JsonFile, NamespaceFile):
    """Class representing a data pack recipe."""

    scope = ("recipes",)
    extension = ".json"


@dataclass(eq=False)
class Structure(BinaryFileBase[StructureFileData], NamespaceFile):
    """Class representing a data pack structure file."""

    content: BinaryFileContent[StructureFileData] = None

    scope = ("structures",)
    extension = ".nbt"

    data = FileDeserialize[StructureFileData]()

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


class TagFile(JsonFile, NamespaceFile):
    """Base class for data pack tag files."""

    extension = ".json"

    def merge(self: TagFileType, other: TagFileType) -> bool:
        if other.data.get("replace"):
            self.data["replace"] = True

        values = self.data.setdefault("values", [])

        for value in other.data.get("values", []):
            if value not in values:
                values.append(deepcopy(value))
        return True


class BlockTag(TagFile):
    """Class representing a data pack block tag."""

    scope = ("tags", "blocks")


class EntityTypeTag(TagFile):
    """Class representing a data pack entity tag."""

    scope = ("tags", "entity_types")


class FluidTag(TagFile):
    """Class representing a data pack fluid tag."""

    scope = ("tags", "fluids")


class FunctionTag(TagFile):
    """Class representing a data pack function tag."""

    scope = ("tags", "functions")


class ItemTag(TagFile):
    """Class representing a data pack item tag."""

    scope = ("tags", "items")


class DimensionType(JsonFile, NamespaceFile):
    """Class representing a data pack dimension type."""

    scope = ("dimension_type",)
    extension = ".json"


class Dimension(JsonFile, NamespaceFile):
    """Class representing a data pack dimension."""

    scope = ("dimension",)
    extension = ".json"


class Biome(JsonFile, NamespaceFile):
    """Class representing a data pack biome."""

    scope = ("worldgen", "biome")
    extension = ".json"


class ConfiguredCarver(JsonFile, NamespaceFile):
    """Class representing a data pack worldgen carver."""

    scope = ("worldgen", "configured_carver")
    extension = ".json"


class ConfiguredFeature(JsonFile, NamespaceFile):
    """Class representing a data pack worldgen feature."""

    scope = ("worldgen", "configured_feature")
    extension = ".json"


class ConfiguredStructureFeature(JsonFile, NamespaceFile):
    """Class representing a data pack worldgen structure feature."""

    scope = ("worldgen", "configured_structure_feature")
    extension = ".json"


class ConfiguredSurfaceBuilder(JsonFile, NamespaceFile):
    """Class representing a data pack worldgen surface builder."""

    scope = ("worldgen", "configured_surface_builder")
    extension = ".json"


class NoiseSettings(JsonFile, NamespaceFile):
    """Class representing a data pack worldgen noise settings."""

    scope = ("worldgen", "noise_settings")
    extension = ".json"


class ProcessorList(JsonFile, NamespaceFile):
    """Class representing a data pack worldgen processor list."""

    scope = ("worldgen", "processor_list")
    extension = ".json"


class TemplatePool(JsonFile, NamespaceFile):
    """Class representing a data pack worldgen template pool."""

    scope = ("worldgen", "template_pool")
    extension = ".json"


class DataPackNamespace(Namespace):
    """Class representing a data pack namespace."""

    directory = "data"

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


class DataPack(Pack[DataPackNamespace]):
    """Class representing a data pack."""

    default_name = "untitled_data_pack"
    latest_pack_format = 6

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
