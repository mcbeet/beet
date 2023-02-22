"""Plugin for experimental worldgen."""


__all__ = [
    "worldgen",
    "Dimension",
    "DimensionType",
    "WorldgenBiome",
    "WorldgenConfiguredCarver",
    "WorldgenConfiguredFeature",
    "WorldgenStructure",
    "WorldgenConfiguredSurfaceBuilder",
    "WorldgenDensityFunction",
    "WorldgenNoise",
    "WorldgenNoiseSettings",
    "WorldgenPlacedFeature",
    "WorldgenProcessorList",
    "WorldgenTemplatePool",
    "WorldgenStructureSet",
    "WorldgenBiomeTag",
    "WorldgenStructureSetTag",
    "WorldgenStructureTag",
    "WorldgenConfiguredCarverTag",
    "WorldgenPlacedFeatureTag",
]


from typing import ClassVar

from beet import Context, DataPack, JsonFileBase, TagFileBase
from beet.core.utils import JsonDict


def beet_default(ctx: Context):
    ctx.require(worldgen)


def worldgen(pack: Context | DataPack):
    """Enable worldgen."""
    if isinstance(pack, Context):
        pack = pack.data

    pack.extend_namespace += [
        Dimension,
        DimensionType,
        WorldgenBiome,
        WorldgenConfiguredCarver,
        WorldgenConfiguredFeature,
        WorldgenStructure,
        WorldgenConfiguredSurfaceBuilder,
        WorldgenDensityFunction,
        WorldgenNoise,
        WorldgenNoiseSettings,
        WorldgenPlacedFeature,
        WorldgenProcessorList,
        WorldgenTemplatePool,
        WorldgenStructureSet,
        WorldgenBiomeTag,
        WorldgenStructureSetTag,
        WorldgenStructureTag,
        WorldgenConfiguredCarverTag,
        WorldgenPlacedFeatureTag,
    ]


class Dimension(JsonFileBase[JsonDict]):
    """Class representing a dimension."""

    scope: ClassVar[tuple[str, ...]] = ("dimension",)
    extension: ClassVar[str] = ".json"


class DimensionType(JsonFileBase[JsonDict]):
    """Class representing a dimension type."""

    scope: ClassVar[tuple[str, ...]] = ("dimension_type",)
    extension: ClassVar[str] = ".json"


class WorldgenBiome(JsonFileBase[JsonDict]):
    """Class representing a biome."""

    scope: ClassVar[tuple[str, ...]] = ("worldgen", "biome")
    extension: ClassVar[str] = ".json"


class WorldgenConfiguredCarver(JsonFileBase[JsonDict]):
    """Class representing a worldgen carver."""

    scope: ClassVar[tuple[str, ...]] = ("worldgen", "configured_carver")
    extension: ClassVar[str] = ".json"


class WorldgenConfiguredFeature(JsonFileBase[JsonDict]):
    """Class representing a worldgen feature."""

    scope: ClassVar[tuple[str, ...]] = ("worldgen", "configured_feature")
    extension: ClassVar[str] = ".json"


class WorldgenStructure(JsonFileBase[JsonDict]):
    """Class representing a worldgen structure feature."""

    scope: ClassVar[tuple[str, ...]] = ("worldgen", "structure")
    extension: ClassVar[str] = ".json"


class WorldgenConfiguredSurfaceBuilder(JsonFileBase[JsonDict]):
    """Class representing a worldgen surface builder."""

    scope: ClassVar[tuple[str, ...]] = ("worldgen", "configured_surface_builder")
    extension: ClassVar[str] = ".json"


class WorldgenDensityFunction(JsonFileBase[JsonDict]):
    """Class representing a density function."""

    scope: ClassVar[tuple[str, ...]] = ("worldgen", "density_function")
    extension: ClassVar[str] = ".json"


class WorldgenNoise(JsonFileBase[JsonDict]):
    """Class representing a worldgen noise."""

    scope: ClassVar[tuple[str, ...]] = ("worldgen", "noise")
    extension: ClassVar[str] = ".json"


class WorldgenNoiseSettings(JsonFileBase[JsonDict]):
    """Class representing worldgen noise settings."""

    scope: ClassVar[tuple[str, ...]] = ("worldgen", "noise_settings")
    extension: ClassVar[str] = ".json"


class WorldgenPlacedFeature(JsonFileBase[JsonDict]):
    """Class representing a placed feature."""

    scope: ClassVar[tuple[str, ...]] = ("worldgen", "placed_feature")
    extension: ClassVar[str] = ".json"


class WorldgenProcessorList(JsonFileBase[JsonDict]):
    """Class representing a worldgen processor list."""

    scope: ClassVar[tuple[str, ...]] = ("worldgen", "processor_list")
    extension: ClassVar[str] = ".json"


class WorldgenTemplatePool(JsonFileBase[JsonDict]):
    """Class representing a worldgen template pool."""

    scope: ClassVar[tuple[str, ...]] = ("worldgen", "template_pool")
    extension: ClassVar[str] = ".json"


class WorldgenStructureSet(JsonFileBase[JsonDict]):
    """Class representing a worldgen structure set."""

    scope: ClassVar[tuple[str, ...]] = ("worldgen", "structure_set")
    extension: ClassVar[str] = ".json"


class WorldgenBiomeTag(TagFileBase):
    """Class representing a biome tag."""

    scope: ClassVar[tuple[str, ...]] = ("tags", "worldgen", "biome")


class WorldgenStructureSetTag(TagFileBase):
    """Class representing a worldgen structure set tag."""

    scope: ClassVar[tuple[str, ...]] = ("tags", "worldgen", "structure_set")


class WorldgenStructureTag(TagFileBase):
    """Class representing a worldgen structure feature tag."""

    scope: ClassVar[tuple[str, ...]] = ("tags", "worldgen", "structure")


class WorldgenConfiguredCarverTag(TagFileBase):
    """Class representing a worldgen carver tag."""

    scope: ClassVar[tuple[str, ...]] = ("tags", "worldgen", "configured_carver")


class WorldgenPlacedFeatureTag(TagFileBase):
    """Class representing a worldgen placed feature tag."""

    scope: ClassVar[tuple[str, ...]] = ("tags", "worldgen", "placed_feature")
