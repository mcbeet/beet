__all__ = [
    "DataPack",
    "DataPackNamespace",
    "Advancement",
    "Function",
    "ItemModifier",
    "LootTable",
    "Predicate",
    "Recipe",
    "Structure",
    "TagFile",
    "BlockTag",
    "EntityTypeTag",
    "FluidTag",
    "FunctionTag",
    "GameEventTag",
    "ItemTag",
]


import io
from copy import deepcopy
from dataclasses import dataclass
from gzip import GzipFile
from typing import ClassVar, Iterable, List, Optional, Tuple, TypeVar, Union

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
    NamespacePin,
    NamespaceProxyDescriptor,
    Pack,
)

TagFileType = TypeVar("TagFileType", bound="TagFile")


class Advancement(JsonFile):
    """Class representing an advancement."""

    scope: ClassVar[Tuple[str, ...]] = ("advancements",)
    extension: ClassVar[str] = ".json"


@dataclass(eq=False, repr=False)
class Function(TextFileBase[List[str]]):
    """Class representing a function."""

    content: TextFileContent[List[str]] = None
    tags: Optional[List[str]] = extra_field(default=None)
    prepend_tags: Optional[List[str]] = extra_field(default=None)

    scope: ClassVar[Tuple[str, ...]] = ("functions",)
    extension: ClassVar[str] = ".mcfunction"

    lines: ClassVar[FileDeserialize[List[str]]] = FileDeserialize()

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

    def to_str(self, content: List[str]) -> str:
        return "\n".join(content) + "\n"

    def from_str(self, content: str) -> List[str]:
        return content.splitlines()

    def bind(self, pack: "DataPack", path: str):
        super().bind(pack, path)

        for tag_name in self.tags or ():
            pack.function_tags.merge({tag_name: FunctionTag({"values": [path]})})

        for tag_name in self.prepend_tags or ():
            function_tag = pack.function_tags.setdefault(tag_name, FunctionTag())
            function_tag.prepend(FunctionTag({"values": [path]}))


class ItemModifier(JsonFile):
    """Class representing an item modifier."""

    scope: ClassVar[Tuple[str, ...]] = ("item_modifiers",)
    extension: ClassVar[str] = ".json"


class LootTable(JsonFile):
    """Class representing a loot table."""

    scope: ClassVar[Tuple[str, ...]] = ("loot_tables",)
    extension: ClassVar[str] = ".json"


class Predicate(JsonFile):
    """Class representing a predicate."""

    scope: ClassVar[Tuple[str, ...]] = ("predicates",)
    extension: ClassVar[str] = ".json"


class Recipe(JsonFile):
    """Class representing a recipe."""

    scope: ClassVar[Tuple[str, ...]] = ("recipes",)
    extension: ClassVar[str] = ".json"


@dataclass(eq=False, repr=False)
class Structure(BinaryFileBase[StructureFileData]):
    """Class representing a structure file."""

    content: BinaryFileContent[StructureFileData] = None

    scope: ClassVar[Tuple[str, ...]] = ("structures",)
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

    scope: ClassVar[Tuple[str, ...]] = ("tags", "blocks")


class EntityTypeTag(TagFile):
    """Class representing an entity tag."""

    scope: ClassVar[Tuple[str, ...]] = ("tags", "entity_types")


class FluidTag(TagFile):
    """Class representing a fluid tag."""

    scope: ClassVar[Tuple[str, ...]] = ("tags", "fluids")


class FunctionTag(TagFile):
    """Class representing a function tag."""

    scope: ClassVar[Tuple[str, ...]] = ("tags", "functions")


class GameEventTag(TagFile):
    """Class representing a game event tag."""

    scope: ClassVar[Tuple[str, ...]] = ("tags", "game_events")


class ItemTag(TagFile):
    """Class representing an item tag."""

    scope: ClassVar[Tuple[str, ...]] = ("tags", "items")


class DataPackNamespace(Namespace):
    """Class representing a data pack namespace."""

    directory = "data"

    # fmt: off
    advancements:     NamespacePin[Advancement]   = NamespacePin(Advancement)
    functions:        NamespacePin[Function]      = NamespacePin(Function)
    loot_tables:      NamespacePin[LootTable]     = NamespacePin(LootTable)
    predicates:       NamespacePin[Predicate]     = NamespacePin(Predicate)
    recipes:          NamespacePin[Recipe]        = NamespacePin(Recipe)
    structures:       NamespacePin[Structure]     = NamespacePin(Structure)
    block_tags:       NamespacePin[BlockTag]      = NamespacePin(BlockTag)
    entity_type_tags: NamespacePin[EntityTypeTag] = NamespacePin(EntityTypeTag)
    fluid_tags:       NamespacePin[FluidTag]      = NamespacePin(FluidTag)
    function_tags:    NamespacePin[FunctionTag]   = NamespacePin(FunctionTag)
    game_event_tags:  NamespacePin[GameEventTag]  = NamespacePin(GameEventTag)
    item_tags:        NamespacePin[ItemTag]       = NamespacePin(ItemTag)
    item_modifiers:   NamespacePin[ItemModifier]  = NamespacePin(ItemModifier)
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
        (1, 19): 10,
    }
    latest_pack_format = pack_format_registry[split_version(LATEST_MINECRAFT_VERSION)]

    # fmt: off
    advancements:     NamespaceProxyDescriptor[Advancement]   = NamespaceProxyDescriptor(Advancement)
    functions:        NamespaceProxyDescriptor[Function]      = NamespaceProxyDescriptor(Function)
    loot_tables:      NamespaceProxyDescriptor[LootTable]     = NamespaceProxyDescriptor(LootTable)
    predicates:       NamespaceProxyDescriptor[Predicate]     = NamespaceProxyDescriptor(Predicate)
    recipes:          NamespaceProxyDescriptor[Recipe]        = NamespaceProxyDescriptor(Recipe)
    structures:       NamespaceProxyDescriptor[Structure]     = NamespaceProxyDescriptor(Structure)
    block_tags:       NamespaceProxyDescriptor[BlockTag]      = NamespaceProxyDescriptor(BlockTag)
    entity_type_tags: NamespaceProxyDescriptor[EntityTypeTag] = NamespaceProxyDescriptor(EntityTypeTag)
    fluid_tags:       NamespaceProxyDescriptor[FluidTag]      = NamespaceProxyDescriptor(FluidTag)
    function_tags:    NamespaceProxyDescriptor[FunctionTag]   = NamespaceProxyDescriptor(FunctionTag)
    game_event_tags:  NamespaceProxyDescriptor[GameEventTag]  = NamespaceProxyDescriptor(GameEventTag)
    item_tags:        NamespaceProxyDescriptor[ItemTag]       = NamespaceProxyDescriptor(ItemTag)
    item_modifiers:   NamespaceProxyDescriptor[ItemModifier]  = NamespaceProxyDescriptor(ItemModifier)
    # fmt: on
