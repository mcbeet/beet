__all__ = [
    "DataPack",
    "DataPackNamespace",
    "Advancement",
    "DamageType",
    "ChatType",
    "BannerPattern",
    "WolfVariant",
    "Enchantment",
    "EnchantmentProvider",
    "JukeboxSong",
    "PaintingVariant",
    "WolfVariant",
    "Function",
    "ItemModifier",
    "LootTable",
    "Predicate",
    "Recipe",
    "Structure",
    "TrimPattern",
    "TrimMaterial",
    "FrogVariant",
    "CatVariant",
    "CowVariant",
    "ChickenVariant",
    "WolfSoundVariant",
    "TagFile",
    "BlockTag",
    "EntityTypeTag",
    "FluidTag",
    "FunctionTag",
    "GameEventTag",
    "ItemTag",
    "ChatTypeTag",
    "DamageTypeTag",
    "BannerPattern",
    "BannerPatternTag",
    "CatVariantTag",
    "EnchantmentTag",
    "InstrumentTag",
    "PaintingVariantTag",
    "PointOfInterestTypeTag",
    "Instrument",
    "TrialSpawner",
]


import io
from copy import deepcopy
from dataclasses import dataclass
from gzip import GzipFile
from typing import ClassVar, Iterable, List, Optional, TypeVar, Union

from nbtlib.contrib.minecraft import StructureFile, StructureFileData

from beet.core.file import (
    BinaryFileBase,
    BinaryFileContent,
    FileDeserialize,
    JsonFile,
    TextFileBase,
    TextFileContent,
)
from beet.core.utils import JsonDict, extra_field, split_version

from .base import (
    LATEST_MINECRAFT_VERSION,
    Namespace,
    NamespaceFileScope,
    NamespacePin,
    NamespaceProxyDescriptor,
    Pack,
)

TagFileType = TypeVar("TagFileType", bound="TagFile")


class Advancement(JsonFile):
    """Class representing an advancement."""

    scope: ClassVar[NamespaceFileScope] = {
        0: ("advancements",),
        45: ("advancement",),
    }
    extension: ClassVar[str] = ".json"


class DamageType(JsonFile):
    """Class representing a damage type."""

    scope: ClassVar[NamespaceFileScope] = ("damage_type",)
    extension: ClassVar[str] = ".json"


class ChatType(JsonFile):
    """Class representing a chat type."""

    scope: ClassVar[NamespaceFileScope] = ("chat_type",)
    extension: ClassVar[str] = ".json"


class BannerPattern(JsonFile):
    """Class representing a banner pattern."""

    scope: ClassVar[NamespaceFileScope] = ("banner_pattern",)
    extension: ClassVar[str] = ".json"


class WolfVariant(JsonFile):
    """Class representing a wolf variant."""

    scope: ClassVar[NamespaceFileScope] = ("wolf_variant",)
    extension: ClassVar[str] = ".json"


class Enchantment(JsonFile):
    """Class representing an enchantment"""

    scope: ClassVar[NamespaceFileScope] = ("enchantment",)
    extension: ClassVar[str] = ".json"


class EnchantmentProvider(JsonFile):
    """Class representing an enchantment provider."""

    scope: ClassVar[NamespaceFileScope] = ("enchantment_provider",)
    extension: ClassVar[str] = ".json"


class JukeboxSong(JsonFile):
    """Class representing a jukebox song."""

    scope: ClassVar[NamespaceFileScope] = ("jukebox_song",)
    extension: ClassVar[str] = ".json"


class PaintingVariant(JsonFile):
    """Class representing a painting variant."""

    scope: ClassVar[NamespaceFileScope] = ("painting_variant",)
    extension: ClassVar[str] = ".json"


class Instrument(JsonFile):
    """Class representing an instrument."""

    scope: ClassVar[NamespaceFileScope] = ("instrument",)
    extension: ClassVar[str] = ".json"


class TrialSpawner(JsonFile):
    """Class representing a trial spawner config."""

    scope: ClassVar[NamespaceFileScope] = ("trial_spawner",)
    extension: ClassVar[str] = ".json"


class FrogVariant(JsonFile):
    """Class representing a frog variant."""

    scope: ClassVar[NamespaceFileScope] = ("frog_variant",)
    extension: ClassVar[str] = ".json"


class CatVariant(JsonFile):
    """Class representing a cat variant."""

    scope: ClassVar[NamespaceFileScope] = ("cat_variant",)
    extension: ClassVar[str] = ".json"


class CowVariant(JsonFile):
    """Class representing a cow variant."""

    scope: ClassVar[NamespaceFileScope] = ("cow_variant",)
    extension: ClassVar[str] = ".json"


class ChickenVariant(JsonFile):
    """Class representing a chicken variant."""

    scope: ClassVar[NamespaceFileScope] = ("chicken_variant",)
    extension: ClassVar[str] = ".json"


class WolfSoundVariant(JsonFile):
    """Class representing a wolf sound variant."""

    scope: ClassVar[NamespaceFileScope] = ("wolf_sound_variant",)
    extension: ClassVar[str] = ".json"


@dataclass(eq=False, repr=False)
class Function(TextFileBase[List[str]]):
    """Class representing a function."""

    content: TextFileContent[List[str]] = None
    tags: Optional[List[str]] = extra_field(default=None)
    prepend_tags: Optional[List[str]] = extra_field(default=None)

    scope: ClassVar[NamespaceFileScope] = {
        0: ("functions",),
        45: ("function",),
    }
    extension: ClassVar[str] = ".mcfunction"

    lines: ClassVar[FileDeserialize[List[str]]] = FileDeserialize()

    def append(self, other: Union["Function", Iterable[str], str]):
        """Append lines from another function."""
        self.lines.extend(
            other.lines
            if isinstance(other, Function)
            else [other] if isinstance(other, str) else other
        )

    def prepend(self, other: Union["Function", Iterable[str], str]):
        """Prepend lines from another function."""
        self.lines[0:0] = (
            other.lines
            if isinstance(other, Function)
            else [other] if isinstance(other, str) else other
        )

    @classmethod
    def default(cls) -> List[str]:
        return []

    def to_str(self, content: List[str]) -> str:
        return "\n".join(content) + "\n"

    def from_str(self, content: str) -> List[str]:
        return content.splitlines()

    def bind(self, pack: "DataPack", path: str):
        super().bind(pack, path)

        for tag_name in self.tags or ():
            pack.function_tags.merge({tag_name: FunctionTag({"values": [path]})})
        self.tags = None

        for tag_name in self.prepend_tags or ():
            function_tag = pack.function_tags.setdefault(tag_name, FunctionTag())
            function_tag.prepend(FunctionTag({"values": [path]}))
        self.prepend_tags = None


class ItemModifier(JsonFile):
    """Class representing an item modifier."""

    scope: ClassVar[NamespaceFileScope] = {
        0: ("item_modifiers",),
        45: ("item_modifier",),
    }
    extension: ClassVar[str] = ".json"


class LootTable(JsonFile):
    """Class representing a loot table."""

    scope: ClassVar[NamespaceFileScope] = {
        0: ("loot_tables",),
        45: ("loot_table",),
    }
    extension: ClassVar[str] = ".json"


class Predicate(JsonFile):
    """Class representing a predicate."""

    scope: ClassVar[NamespaceFileScope] = {
        0: ("predicates",),
        45: ("predicate",),
    }
    extension: ClassVar[str] = ".json"


class Recipe(JsonFile):
    """Class representing a recipe."""

    scope: ClassVar[NamespaceFileScope] = {
        0: ("recipes",),
        45: ("recipe",),
    }
    extension: ClassVar[str] = ".json"


@dataclass(eq=False, repr=False)
class Structure(BinaryFileBase[StructureFileData]):
    """Class representing a structure file."""

    content: BinaryFileContent[StructureFileData] = None

    scope: ClassVar[NamespaceFileScope] = {
        0: ("structures",),
        45: ("structure",),
    }
    extension: ClassVar[str] = ".nbt"

    data: ClassVar[FileDeserialize[StructureFileData]] = FileDeserialize()

    def from_bytes(self, content: bytes) -> StructureFileData:
        with GzipFile(fileobj=io.BytesIO(content)) as fileobj:
            return StructureFile.parse(fileobj).root

    def to_bytes(self, content: StructureFileData) -> bytes:
        dst = io.BytesIO()
        with GzipFile(fileobj=dst, mode="wb") as fileobj:
            StructureFile(content).write(fileobj)
        return dst.getvalue()


class TrimPattern(JsonFile):
    """Class representing a trim pattern."""

    scope: ClassVar[NamespaceFileScope] = ("trim_pattern",)
    extension: ClassVar[str] = ".json"


class TrimMaterial(JsonFile):
    """Class representing a trim material."""

    scope: ClassVar[NamespaceFileScope] = ("trim_material",)
    extension: ClassVar[str] = ".json"


class TagFile(JsonFile):
    """Base class for tag files."""

    extension: ClassVar[str] = ".json"

    def merge(self: TagFileType, other: TagFileType) -> bool:  # type: ignore
        if other.data.get("replace"):
            self.data["replace"] = True
            self.data["values"] = deepcopy(other.data.get("values", []))
            return True

        values = self.data.setdefault("values", [])

        for value in other.data.get("values", []):
            if value not in values:
                values.append(deepcopy(value))
        return True

    def append(self: TagFileType, other: TagFileType):
        """Append values from another tag."""
        self.merge(other)

    def prepend(self: TagFileType, other: TagFileType):
        """Prepend values from another tag."""
        if other.data.get("replace"):
            self.data["replace"] = True
            self.data["values"] = deepcopy(other.data.get("values", []))
            return

        values = self.data.setdefault("values", [])

        for value in other.data.get("values", []):
            if value not in values:
                values.insert(0, deepcopy(value))

    def add(self, value: str):
        """Add an entry."""
        values = self.data.setdefault("values", [])
        if value not in values:
            values.append(value)

    def remove(self, value: str):
        """Remove an entry."""
        values = self.data.setdefault("values", [])
        try:
            values.remove(value)
        except ValueError:
            pass

    @classmethod
    def default(cls) -> JsonDict:
        return {"values": []}


class BlockTag(TagFile):
    """Class representing a block tag."""

    scope: ClassVar[NamespaceFileScope] = {
        0: ("tags", "blocks"),
        45: ("tags", "block"),
    }


class EntityTypeTag(TagFile):
    """Class representing an entity tag."""

    scope: ClassVar[NamespaceFileScope] = {
        0: ("tags", "entity_types"),
        45: ("tags", "entity_type"),
    }


class FluidTag(TagFile):
    """Class representing a fluid tag."""

    scope: ClassVar[NamespaceFileScope] = {
        0: ("tags", "fluids"),
        45: ("tags", "fluid"),
    }


class FunctionTag(TagFile):
    """Class representing a function tag."""

    scope: ClassVar[NamespaceFileScope] = {
        0: ("tags", "functions"),
        45: ("tags", "function"),
    }


class GameEventTag(TagFile):
    """Class representing a game event tag."""

    scope: ClassVar[NamespaceFileScope] = {
        0: ("tags", "game_events"),
        45: ("tags", "game_event"),
    }


class ItemTag(TagFile):
    """Class representing an item tag."""

    scope: ClassVar[NamespaceFileScope] = {
        0: ("tags", "items"),
        45: ("tags", "item"),
    }


class ChatTypeTag(TagFile):
    """Class representing a chat type tag."""

    scope: ClassVar[NamespaceFileScope] = (
        "tags",
        "chat_type",
    )


class DamageTypeTag(TagFile):
    """Class representing a damage type tag."""

    scope: ClassVar[NamespaceFileScope] = (
        "tags",
        "damage_type",
    )


class BannerPatternTag(TagFile):
    """Class representing a banner pattern tag."""

    scope: ClassVar[NamespaceFileScope] = (
        "tags",
        "banner_pattern",
    )


class CatVariantTag(TagFile):
    """Class representing a cat variant tag."""

    scope: ClassVar[NamespaceFileScope] = (
        "tags",
        "cat_variant",
    )


class EnchantmentTag(TagFile):
    """Class representing an enchantment tag."""

    scope: ClassVar[NamespaceFileScope] = (
        "tags",
        "enchantment",
    )


class InstrumentTag(TagFile):
    """Class representing an instrument tag."""

    scope: ClassVar[NamespaceFileScope] = (
        "tags",
        "instrument",
    )


class PaintingVariantTag(TagFile):
    """Class representing a painting variant tag."""

    scope: ClassVar[NamespaceFileScope] = (
        "tags",
        "painting_variant",
    )


class PointOfInterestTypeTag(TagFile):
    """Class representing a point of interest type tag."""

    scope: ClassVar[NamespaceFileScope] = (
        "tags",
        "point_of_interest_type",
    )


class FrogVariantTag(TagFile):
    """Class representing a frog variant tag."""

    scope: ClassVar[NamespaceFileScope] = (
        "tags",
        "frog_variant",
    )


class CowVariantTag(TagFile):
    """Class representing a cow variant tag."""

    scope: ClassVar[NamespaceFileScope] = (
        "tags",
        "cow_variant",
    )


class ChickenVariantTag(TagFile):
    """Class representing a chicken variant tag."""

    scope: ClassVar[NamespaceFileScope] = (
        "tags",
        "chicken_variant",
    )


class WolfSoundVariantTag(TagFile):
    """Class representing a wolf sound variant tag."""

    scope: ClassVar[NamespaceFileScope] = (
        "tags",
        "wolf_sound_variant",
    )


class DataPackNamespace(Namespace):
    """Class representing a data pack namespace."""

    directory = "data"

    # fmt: off
    advancements:                       NamespacePin[Advancement]               = NamespacePin(Advancement)
    functions:                          NamespacePin[Function]                  = NamespacePin(Function)
    item_modifiers:                     NamespacePin[ItemModifier]              = NamespacePin(ItemModifier)
    loot_tables:                        NamespacePin[LootTable]                 = NamespacePin(LootTable)
    predicates:                         NamespacePin[Predicate]                 = NamespacePin(Predicate)
    recipes:                            NamespacePin[Recipe]                    = NamespacePin(Recipe)
    trim_pattern:                       NamespacePin[TrimPattern]               = NamespacePin(TrimPattern)
    trim_material:                      NamespacePin[TrimMaterial]              = NamespacePin(TrimMaterial)
    structures:                         NamespacePin[Structure]                 = NamespacePin(Structure)
    chat_type:                          NamespacePin[ChatType]                  = NamespacePin(ChatType)
    damage_type:                        NamespacePin[DamageType]                = NamespacePin(DamageType)
    banner_patterns:                    NamespacePin[BannerPattern]             = NamespacePin(BannerPattern)
    wolf_variants:                      NamespacePin[WolfVariant]               = NamespacePin(WolfVariant)
    enchantments:                       NamespacePin[Enchantment]               = NamespacePin(Enchantment)
    enchantment_providers:              NamespacePin[EnchantmentProvider]       = NamespacePin(EnchantmentProvider)
    jukebox_songs:                      NamespacePin[JukeboxSong]               = NamespacePin(JukeboxSong)
    painting_variants:                  NamespacePin[PaintingVariant]           = NamespacePin(PaintingVariant)
    instruments:                        NamespacePin[Instrument]                = NamespacePin(Instrument)
    trial_spawners:                     NamespacePin[TrialSpawner]              = NamespacePin(TrialSpawner)
    frog_variants:                      NamespacePin[FrogVariant]               = NamespacePin(FrogVariant)
    cat_variants:                       NamespacePin[CatVariant]                = NamespacePin(CatVariant)
    cow_variants:                       NamespacePin[CowVariant]                = NamespacePin(CowVariant)
    chicken_variants:                   NamespacePin[ChickenVariant]            = NamespacePin(ChickenVariant)
    wolf_sound_variants:                NamespacePin[WolfSoundVariant]          = NamespacePin(WolfSoundVariant)
    block_tags:                         NamespacePin[BlockTag]                  = NamespacePin(BlockTag)
    entity_type_tags:                   NamespacePin[EntityTypeTag]             = NamespacePin(EntityTypeTag)
    fluid_tags:                         NamespacePin[FluidTag]                  = NamespacePin(FluidTag)
    function_tags:                      NamespacePin[FunctionTag]               = NamespacePin(FunctionTag)
    game_event_tags:                    NamespacePin[GameEventTag]              = NamespacePin(GameEventTag)
    item_tags:                          NamespacePin[ItemTag]                   = NamespacePin(ItemTag)
    chat_type_tags:                     NamespacePin[ChatTypeTag]               = NamespacePin(ChatTypeTag)
    damage_type_tags:                   NamespacePin[DamageTypeTag]             = NamespacePin(DamageTypeTag)
    banner_pattern_tags:                NamespacePin[BannerPatternTag]          = NamespacePin(BannerPatternTag)
    cat_variant_tags:                   NamespacePin[CatVariantTag]             = NamespacePin(CatVariantTag)
    enchantment_tags:                   NamespacePin[EnchantmentTag]            = NamespacePin(EnchantmentTag)
    instrument_tags:                    NamespacePin[InstrumentTag]             = NamespacePin(InstrumentTag)
    painting_variant_tags:              NamespacePin[PaintingVariantTag]        = NamespacePin(PaintingVariantTag)
    point_of_interest_type_tags:        NamespacePin[PointOfInterestTypeTag]    = NamespacePin(PointOfInterestTypeTag)
    frog_variant_tags:                  NamespacePin[FrogVariantTag]            = NamespacePin(FrogVariantTag)
    cow_variant_tags:                   NamespacePin[CowVariantTag]             = NamespacePin(CowVariantTag)
    chicken_variant_tags:               NamespacePin[ChickenVariantTag]         = NamespacePin(ChickenVariantTag)
    wolf_sound_variant_tags:            NamespacePin[WolfSoundVariantTag]       = NamespacePin(WolfSoundVariantTag)

    # fmt: on


class DataPack(Pack[DataPackNamespace]):
    """Class representing a data pack."""

    default_name = "untitled_data_pack"

    pack_format_registry = {
        (1, 13): 4,
        (1, 14): 4,
        (1, 15): 5,
        (1, 16): 6,
        (1, 17): 7,
        (1, 18): 9,
        (1, 19): 12,
        (1, 20): 41,
        (1, 21): 71,
    }
    latest_pack_format = pack_format_registry[split_version(LATEST_MINECRAFT_VERSION)]

    # fmt: off
    advancements:                       NamespaceProxyDescriptor[Advancement]               = NamespaceProxyDescriptor(Advancement)
    functions:                          NamespaceProxyDescriptor[Function]                  = NamespaceProxyDescriptor(Function)
    item_modifiers:                     NamespaceProxyDescriptor[ItemModifier]              = NamespaceProxyDescriptor(ItemModifier)
    loot_tables:                        NamespaceProxyDescriptor[LootTable]                 = NamespaceProxyDescriptor(LootTable)
    predicates:                         NamespaceProxyDescriptor[Predicate]                 = NamespaceProxyDescriptor(Predicate)
    recipes:                            NamespaceProxyDescriptor[Recipe]                    = NamespaceProxyDescriptor(Recipe)
    trim_pattern:                       NamespaceProxyDescriptor[TrimPattern]               = NamespaceProxyDescriptor(TrimPattern)
    trim_material:                      NamespaceProxyDescriptor[TrimMaterial]              = NamespaceProxyDescriptor(TrimMaterial)
    structures:                         NamespaceProxyDescriptor[Structure]                 = NamespaceProxyDescriptor(Structure)
    chat_type:                          NamespaceProxyDescriptor[ChatType]                  = NamespaceProxyDescriptor(ChatType)
    damage_type:                        NamespaceProxyDescriptor[DamageType]                = NamespaceProxyDescriptor(DamageType)
    banner_patterns:                    NamespaceProxyDescriptor[BannerPattern]             = NamespaceProxyDescriptor(BannerPattern)
    wolf_variants:                      NamespaceProxyDescriptor[WolfVariant]               = NamespaceProxyDescriptor(WolfVariant)
    enchantments:                       NamespaceProxyDescriptor[Enchantment]               = NamespaceProxyDescriptor(Enchantment)
    enchantment_providers:              NamespaceProxyDescriptor[EnchantmentProvider]       = NamespaceProxyDescriptor(EnchantmentProvider)
    jukebox_songs:                      NamespaceProxyDescriptor[JukeboxSong]               = NamespaceProxyDescriptor(JukeboxSong)
    painting_variants:                  NamespaceProxyDescriptor[PaintingVariant]           = NamespaceProxyDescriptor(PaintingVariant)
    instruments:                        NamespaceProxyDescriptor[Instrument]                = NamespaceProxyDescriptor(Instrument)
    trial_spawners:                     NamespaceProxyDescriptor[TrialSpawner]              = NamespaceProxyDescriptor(TrialSpawner)
    frog_variants:                      NamespaceProxyDescriptor[FrogVariant]               = NamespaceProxyDescriptor(FrogVariant)
    cat_variants:                       NamespaceProxyDescriptor[CatVariant]                = NamespaceProxyDescriptor(CatVariant)
    cow_variants:                       NamespaceProxyDescriptor[CowVariant]                = NamespaceProxyDescriptor(CowVariant)
    chicken_variants:                   NamespaceProxyDescriptor[ChickenVariant]            = NamespaceProxyDescriptor(ChickenVariant)
    wolf_sound_variants:                NamespaceProxyDescriptor[WolfSoundVariant]          = NamespaceProxyDescriptor(WolfSoundVariant)
    block_tags:                         NamespaceProxyDescriptor[BlockTag]                  = NamespaceProxyDescriptor(BlockTag)
    entity_type_tags:                   NamespaceProxyDescriptor[EntityTypeTag]             = NamespaceProxyDescriptor(EntityTypeTag)
    fluid_tags:                         NamespaceProxyDescriptor[FluidTag]                  = NamespaceProxyDescriptor(FluidTag)
    function_tags:                      NamespaceProxyDescriptor[FunctionTag]               = NamespaceProxyDescriptor(FunctionTag)
    game_event_tags:                    NamespaceProxyDescriptor[GameEventTag]              = NamespaceProxyDescriptor(GameEventTag)
    item_tags:                          NamespaceProxyDescriptor[ItemTag]                   = NamespaceProxyDescriptor(ItemTag)
    chat_type_tags:                     NamespaceProxyDescriptor[ChatTypeTag]               = NamespaceProxyDescriptor(ChatTypeTag)
    damage_type_tags:                   NamespaceProxyDescriptor[DamageTypeTag]             = NamespaceProxyDescriptor(DamageTypeTag)
    banner_pattern_tags:                NamespaceProxyDescriptor[BannerPatternTag]          = NamespaceProxyDescriptor(BannerPatternTag)
    cat_variant_tags:                   NamespaceProxyDescriptor[CatVariantTag]             = NamespaceProxyDescriptor(CatVariantTag)
    enchantment_tags:                   NamespaceProxyDescriptor[EnchantmentTag]            = NamespaceProxyDescriptor(EnchantmentTag)
    instrument_tags:                    NamespaceProxyDescriptor[InstrumentTag]             = NamespaceProxyDescriptor(InstrumentTag)
    painting_variant_tags:              NamespaceProxyDescriptor[PaintingVariantTag]        = NamespaceProxyDescriptor(PaintingVariantTag)
    point_of_interest_type_tags:        NamespaceProxyDescriptor[PointOfInterestTypeTag]    = NamespaceProxyDescriptor(PointOfInterestTypeTag)
    frog_variant_tags:                  NamespaceProxyDescriptor[FrogVariantTag]            = NamespaceProxyDescriptor(FrogVariantTag)
    cow_variant_tags:                   NamespaceProxyDescriptor[CowVariantTag]             = NamespaceProxyDescriptor(CowVariantTag)
    chicken_variant_tags:               NamespaceProxyDescriptor[ChickenVariantTag]         = NamespaceProxyDescriptor(ChickenVariantTag)
    wolf_sound_variant_tags:            NamespaceProxyDescriptor[WolfSoundVariantTag]       = NamespaceProxyDescriptor(WolfSoundVariantTag)
    # fmt: on
