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
    "ItemModifier",
]


import io
from copy import deepcopy
from dataclasses import dataclass
from gzip import GzipFile
from typing import Iterable, List, Optional, TypeVar, Union

from nbtlib.contrib.minecraft import StructureFile, StructureFileData

from beet.core.file import (
    BinaryFileBase,
    BinaryFileContent,
    FileDeserialize,
    JsonFile,
    TextFileBase,
    TextFileContent,
)
from beet.core.utils import JsonDict, extra_field

from .base import Namespace, NamespaceFile, NamespacePin, NamespaceProxyDescriptor, Pack

TagFileType = TypeVar("TagFileType", bound="TagFile")


class Advancement(JsonFile, NamespaceFile):
    """Class representing an advancement."""

    scope = ("advancements",)
    extension = ".json"


@dataclass(eq=False)
class Function(TextFileBase[List[str]], NamespaceFile):
    """Class representing a function."""

    content: TextFileContent[List[str]] = None
    tags: Optional[List[str]] = extra_field(default=None)
    prepend_tags: Optional[List[str]] = extra_field(default=None)

    scope = ("functions",)
    extension = ".mcfunction"

    lines = FileDeserialize()  # type: FileDeserialize[List[str]]

    def append(self, other: Union["Function", Iterable[str], str]):
        """Append lines from another function."""
        self.lines.extend(
            other.lines
            if isinstance(other, Function)
            else [other]
            if isinstance(other, str)
            else other
        )

    def prepend(self, other: Union["Function", Iterable[str], str]):
        """Prepend lines from another function."""
        self.lines[0:0] = (
            other.lines
            if isinstance(other, Function)
            else [other]
            if isinstance(other, str)
            else other
        )

    @classmethod
    def default(cls) -> List[str]:
        return []

    @classmethod
    def to_str(cls, content: List[str]) -> str:
        return "\n".join(content) + "\n"

    @classmethod
    def from_str(cls, content: str) -> List[str]:
        return content.splitlines()

    def bind(self, pack: "DataPack", namespace: str, path: str):
        super().bind(pack, namespace, path)

        for tag_name in self.tags or ():
            pack.function_tags.merge(
                {tag_name: FunctionTag({"values": [f"{namespace}:{path}"]})}
            )

        for tag_name in self.prepend_tags or ():
            function_tag = pack.function_tags.setdefault(tag_name, FunctionTag())
            function_tag.prepend(FunctionTag({"values": [f"{namespace}:{path}"]}))


class LootTable(JsonFile, NamespaceFile):
    """Class representing a loot table."""

    scope = ("loot_tables",)
    extension = ".json"


class Predicate(JsonFile, NamespaceFile):
    """Class representing a predicate."""

    scope = ("predicates",)
    extension = ".json"


class Recipe(JsonFile, NamespaceFile):
    """Class representing a recipe."""

    scope = ("recipes",)
    extension = ".json"


@dataclass(eq=False)
class Structure(BinaryFileBase[StructureFileData], NamespaceFile):
    """Class representing a structure file."""

    content: BinaryFileContent[StructureFileData] = None

    scope = ("structures",)
    extension = ".nbt"

    data = FileDeserialize()  # type: FileDeserialize[StructureFileData]

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
    """Base class for tag files."""

    extension = ".json"

    def merge(self: TagFileType, other: TagFileType) -> bool:  # type: ignore
        if other.data.get("replace"):
            self.data["replace"] = True

        values = self.data.setdefault("values", [])

        for value in other.data.get("values", []):
            if value not in values:
                values.append(deepcopy(value))
        return True

    def prepend(self: TagFileType, other: TagFileType) -> bool:  # type: ignore
        """Prepend values from another tag."""
        if other.data.get("replace"):
            self.data["replace"] = True

        values = self.data.setdefault("values", [])

        for value in other.data.get("values", []):
            if value not in values:
                values.insert(0, deepcopy(value))

    @classmethod
    def default(cls) -> JsonDict:
        return {"values": []}


class BlockTag(TagFile):
    """Class representing a block tag."""

    scope = ("tags", "blocks")


class EntityTypeTag(TagFile):
    """Class representing an entity tag."""

    scope = ("tags", "entity_types")


class FluidTag(TagFile):
    """Class representing a fluid tag."""

    scope = ("tags", "fluids")


class FunctionTag(TagFile):
    """Class representing a function tag."""

    scope = ("tags", "functions")


class ItemTag(TagFile):
    """Class representing an item tag."""

    scope = ("tags", "items")


class DimensionType(JsonFile, NamespaceFile):
    """Class representing a dimension type."""

    scope = ("dimension_type",)
    extension = ".json"


class Dimension(JsonFile, NamespaceFile):
    """Class representing a dimension."""

    scope = ("dimension",)
    extension = ".json"


class Biome(JsonFile, NamespaceFile):
    """Class representing a biome."""

    scope = ("worldgen", "biome")
    extension = ".json"


class ConfiguredCarver(JsonFile, NamespaceFile):
    """Class representing a worldgen carver."""

    scope = ("worldgen", "configured_carver")
    extension = ".json"


class ConfiguredFeature(JsonFile, NamespaceFile):
    """Class representing a worldgen feature."""

    scope = ("worldgen", "configured_feature")
    extension = ".json"


class ConfiguredStructureFeature(JsonFile, NamespaceFile):
    """Class representing a worldgen structure feature."""

    scope = ("worldgen", "configured_structure_feature")
    extension = ".json"


class ConfiguredSurfaceBuilder(JsonFile, NamespaceFile):
    """Class representing a worldgen surface builder."""

    scope = ("worldgen", "configured_surface_builder")
    extension = ".json"


class NoiseSettings(JsonFile, NamespaceFile):
    """Class representing worldgen noise settings."""

    scope = ("worldgen", "noise_settings")
    extension = ".json"


class ProcessorList(JsonFile, NamespaceFile):
    """Class representing a worldgen processor list."""

    scope = ("worldgen", "processor_list")
    extension = ".json"


class TemplatePool(JsonFile, NamespaceFile):
    """Class representing a worldgen template pool."""

    scope = ("worldgen", "template_pool")
    extension = ".json"


class ItemModifier(JsonFile, NamespaceFile):
    """Class representing an item modifier."""

    scope = ("item_modifiers",)
    extension = ".json"


class DataPackNamespace(Namespace):
    """Class representing a data pack namespace."""

    directory = "data"

    # fmt: off
    advancements:                  NamespacePin[Advancement]                = NamespacePin(Advancement)
    functions:                     NamespacePin[Function]                   = NamespacePin(Function)
    loot_tables:                   NamespacePin[LootTable]                  = NamespacePin(LootTable)
    predicates:                    NamespacePin[Predicate]                  = NamespacePin(Predicate)
    recipes:                       NamespacePin[Recipe]                     = NamespacePin(Recipe)
    structures:                    NamespacePin[Structure]                  = NamespacePin(Structure)
    block_tags:                    NamespacePin[BlockTag]                   = NamespacePin(BlockTag)
    entity_type_tags:              NamespacePin[EntityTypeTag]              = NamespacePin(EntityTypeTag)
    fluid_tags:                    NamespacePin[FluidTag]                   = NamespacePin(FluidTag)
    function_tags:                 NamespacePin[FunctionTag]                = NamespacePin(FunctionTag)
    item_tags:                     NamespacePin[ItemTag]                    = NamespacePin(ItemTag)
    dimension_types:               NamespacePin[DimensionType]              = NamespacePin(DimensionType)
    dimensions:                    NamespacePin[Dimension]                  = NamespacePin(Dimension)
    biomes:                        NamespacePin[Biome]                      = NamespacePin(Biome)
    configured_carvers:            NamespacePin[ConfiguredCarver]           = NamespacePin(ConfiguredCarver)
    configured_features:           NamespacePin[ConfiguredFeature]          = NamespacePin(ConfiguredFeature)
    configured_structure_features: NamespacePin[ConfiguredStructureFeature] = NamespacePin(ConfiguredStructureFeature)
    configured_surface_builders:   NamespacePin[ConfiguredSurfaceBuilder]   = NamespacePin(ConfiguredSurfaceBuilder)
    noise_settings:                NamespacePin[NoiseSettings]              = NamespacePin(NoiseSettings)
    processor_lists:               NamespacePin[ProcessorList]              = NamespacePin(ProcessorList)
    template_pools:                NamespacePin[TemplatePool]               = NamespacePin(TemplatePool)
    item_modifiers:                NamespacePin[ItemModifier]               = NamespacePin(ItemModifier)
    # fmt: on


class DataPack(Pack[DataPackNamespace]):
    """Class representing a data pack."""

    default_name = "untitled_data_pack"
    latest_pack_format = 7

    # fmt: off
    advancements:                  NamespaceProxyDescriptor[Advancement]                = NamespaceProxyDescriptor(Advancement)
    functions:                     NamespaceProxyDescriptor[Function]                   = NamespaceProxyDescriptor(Function)
    loot_tables:                   NamespaceProxyDescriptor[LootTable]                  = NamespaceProxyDescriptor(LootTable)
    predicates:                    NamespaceProxyDescriptor[Predicate]                  = NamespaceProxyDescriptor(Predicate)
    recipes:                       NamespaceProxyDescriptor[Recipe]                     = NamespaceProxyDescriptor(Recipe)
    structures:                    NamespaceProxyDescriptor[Structure]                  = NamespaceProxyDescriptor(Structure)
    block_tags:                    NamespaceProxyDescriptor[BlockTag]                   = NamespaceProxyDescriptor(BlockTag)
    entity_type_tags:              NamespaceProxyDescriptor[EntityTypeTag]              = NamespaceProxyDescriptor(EntityTypeTag)
    fluid_tags:                    NamespaceProxyDescriptor[FluidTag]                   = NamespaceProxyDescriptor(FluidTag)
    function_tags:                 NamespaceProxyDescriptor[FunctionTag]                = NamespaceProxyDescriptor(FunctionTag)
    item_tags:                     NamespaceProxyDescriptor[ItemTag]                    = NamespaceProxyDescriptor(ItemTag)
    dimension_types:               NamespaceProxyDescriptor[DimensionType]              = NamespaceProxyDescriptor(DimensionType)
    dimensions:                    NamespaceProxyDescriptor[Dimension]                  = NamespaceProxyDescriptor(Dimension)
    biomes:                        NamespaceProxyDescriptor[Biome]                      = NamespaceProxyDescriptor(Biome)
    configured_carvers:            NamespaceProxyDescriptor[ConfiguredCarver]           = NamespaceProxyDescriptor(ConfiguredCarver)
    configured_features:           NamespaceProxyDescriptor[ConfiguredFeature]          = NamespaceProxyDescriptor(ConfiguredFeature)
    configured_structure_features: NamespaceProxyDescriptor[ConfiguredStructureFeature] = NamespaceProxyDescriptor(ConfiguredStructureFeature)
    configured_surface_builders:   NamespaceProxyDescriptor[ConfiguredSurfaceBuilder]   = NamespaceProxyDescriptor(ConfiguredSurfaceBuilder)
    noise_settings:                NamespaceProxyDescriptor[NoiseSettings]              = NamespaceProxyDescriptor(NoiseSettings)
    processor_lists:               NamespaceProxyDescriptor[ProcessorList]              = NamespaceProxyDescriptor(ProcessorList)
    template_pools:                NamespaceProxyDescriptor[TemplatePool]               = NamespaceProxyDescriptor(TemplatePool)
    item_modifiers:                NamespaceProxyDescriptor[ItemModifier]               = NamespaceProxyDescriptor(ItemModifier)
    # fmt: on
