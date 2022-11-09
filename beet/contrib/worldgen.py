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


from typing import ClassVar, Tuple, Union

from beet import Context, DataPack, JsonFile, TagFile


def beet_default(ctx: Context):
    ctx.require(worldgen)


def worldgen(pack: Union[Context, DataPack]):
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


class Dimension(JsonFile):
    """Class representing a dimension."""

    scope: ClassVar[Tuple[str, ...]] = ("dimension",)
    extension: ClassVar[str] = ".json"


class DimensionType(JsonFile):
    """Class representing a dimension type."""

    scope: ClassVar[Tuple[str, ...]] = ("dimension_type",)
    extension: ClassVar[str] = ".json"


class WorldgenBiome(JsonFile):
    """Class representing a biome."""

    scope: ClassVar[Tuple[str, ...]] = ("worldgen", "biome")
    extension: ClassVar[str] = ".json"


class WorldgenConfiguredCarver(JsonFile):
    """Class representing a worldgen carver."""

    scope: ClassVar[Tuple[str, ...]] = ("worldgen", "configured_carver")
    extension: ClassVar[str] = ".json"


class WorldgenConfiguredFeature(JsonFile):
    """Class representing a worldgen feature."""

    scope: ClassVar[Tuple[str, ...]] = ("worldgen", "configured_feature")
    extension: ClassVar[str] = ".json"


class WorldgenStructure(JsonFile):
    """Class representing a worldgen structure feature."""

    scope: ClassVar[Tuple[str, ...]] = ("worldgen", "structure")
    extension: ClassVar[str] = ".json"


class WorldgenConfiguredSurfaceBuilder(JsonFile):
    """Class representing a worldgen surface builder."""

    scope: ClassVar[Tuple[str, ...]] = ("worldgen", "configured_surface_builder")
    extension: ClassVar[str] = ".json"


class WorldgenDensityFunction(JsonFile):
    """Class representing a density function."""

    scope: ClassVar[Tuple[str, ...]] = ("worldgen", "density_function")
    extension: ClassVar[str] = ".json"


class WorldgenNoise(JsonFile):
    """Class representing a worldgen noise."""

    scope: ClassVar[Tuple[str, ...]] = ("worldgen", "noise")
    extension: ClassVar[str] = ".json"


class WorldgenNoiseSettings(JsonFile):
    """Class representing worldgen noise settings."""

    scope: ClassVar[Tuple[str, ...]] = ("worldgen", "noise_settings")
    extension: ClassVar[str] = ".json"


class WorldgenPlacedFeature(JsonFile):
    """Class representing a placed feature."""

    scope: ClassVar[Tuple[str, ...]] = ("worldgen", "placed_feature")
    extension: ClassVar[str] = ".json"


class WorldgenProcessorList(JsonFile):
    """Class representing a worldgen processor list."""

    scope: ClassVar[Tuple[str, ...]] = ("worldgen", "processor_list")
    extension: ClassVar[str] = ".json"


class WorldgenTemplatePool(JsonFile):
    """Class representing a worldgen template pool."""

    scope: ClassVar[Tuple[str, ...]] = ("worldgen", "template_pool")
    extension: ClassVar[str] = ".json"


class WorldgenStructureSet(JsonFile):
    """Class representing a worldgen structure set."""

    scope: ClassVar[Tuple[str, ...]] = ("worldgen", "structure_set")
    extension: ClassVar[str] = ".json"


class WorldgenBiomeTag(TagFile):
    """Class representing a biome tag."""

    scope: ClassVar[Tuple[str, ...]] = ("tags", "worldgen", "biome")


class WorldgenStructureSetTag(TagFile):
    """Class representing a worldgen structure set tag."""

    scope: ClassVar[Tuple[str, ...]] = ("tags", "worldgen", "structure_set")


class WorldgenStructureTag(TagFile):
    """Class representing a worldgen structure feature tag."""

    scope: ClassVar[Tuple[str, ...]] = ("tags", "worldgen", "structure")


class WorldgenConfiguredCarverTag(TagFile):
    """Class representing a worldgen carver tag."""

    scope: ClassVar[Tuple[str, ...]] = ("tags", "worldgen", "configured_carver")


class WorldgenPlacedFeatureTag(TagFile):
    """Class representing a worldgen placed feature tag."""

    scope: ClassVar[Tuple[str, ...]] = ("tags", "worldgen", "placed_feature")
