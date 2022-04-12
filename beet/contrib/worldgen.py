"""Plugin for experimental worldgen."""


__all__ = [
    "worldgen",
    "Dimension",
    "DimensionType",
    "WorldgenBiome",
    "WorldgenConfiguredCarver",
    "WorldgenConfiguredFeature",
    "WorldgenConfiguredStructureFeature",
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
    "WorldgenConfiguredStructureFeatureTag",
    "WorldgenConfiguredCarverTag",
    "WorldgenPlacedFeatureTag",
]


from typing import Union

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
        WorldgenConfiguredStructureFeature,
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
        WorldgenConfiguredStructureFeatureTag,
        WorldgenConfiguredCarverTag,
        WorldgenPlacedFeatureTag,
    ]


class Dimension(JsonFile):
    """Class representing a dimension."""

    scope = ("dimension",)
    extension = ".json"


class DimensionType(JsonFile):
    """Class representing a dimension type."""

    scope = ("dimension_type",)
    extension = ".json"


class WorldgenBiome(JsonFile):
    """Class representing a biome."""

    scope = ("worldgen", "biome")
    extension = ".json"


class WorldgenConfiguredCarver(JsonFile):
    """Class representing a worldgen carver."""

    scope = ("worldgen", "configured_carver")
    extension = ".json"


class WorldgenConfiguredFeature(JsonFile):
    """Class representing a worldgen feature."""

    scope = ("worldgen", "configured_feature")
    extension = ".json"


class WorldgenConfiguredStructureFeature(JsonFile):
    """Class representing a worldgen structure feature."""

    scope = ("worldgen", "configured_structure_feature")
    extension = ".json"


class WorldgenConfiguredSurfaceBuilder(JsonFile):
    """Class representing a worldgen surface builder."""

    scope = ("worldgen", "configured_surface_builder")
    extension = ".json"


class WorldgenDensityFunction(JsonFile):
    """Class representing a density function."""

    scope = ("worldgen", "density_function")
    extension = ".json"


class WorldgenNoise(JsonFile):
    """Class representing a worldgen noise."""

    scope = ("worldgen", "noise")
    extension = ".json"


class WorldgenNoiseSettings(JsonFile):
    """Class representing worldgen noise settings."""

    scope = ("worldgen", "noise_settings")
    extension = ".json"


class WorldgenPlacedFeature(JsonFile):
    """Class representing a placed feature."""

    scope = ("worldgen", "placed_feature")
    extension = ".json"


class WorldgenProcessorList(JsonFile):
    """Class representing a worldgen processor list."""

    scope = ("worldgen", "processor_list")
    extension = ".json"


class WorldgenTemplatePool(JsonFile):
    """Class representing a worldgen template pool."""

    scope = ("worldgen", "template_pool")
    extension = ".json"


class WorldgenStructureSet(JsonFile):
    """Class representing a worldgen structure set."""

    scope = ("worldgen", "structure_set")
    extension = ".json"


class WorldgenBiomeTag(TagFile):
    """Class representing a biome tag."""

    scope = ("tags", "worldgen", "biome")


class WorldgenStructureSetTag(TagFile):
    """Class representing a worldgen structure set tag."""

    scope = ("tags", "worldgen", "structure_set")


class WorldgenConfiguredStructureFeatureTag(TagFile):
    """Class representing a worldgen structure feature tag."""

    scope = ("tags", "worldgen", "configured_structure_feature")


class WorldgenConfiguredCarverTag(TagFile):
    """Class representing a worldgen carver tag."""

    scope = ("tags", "worldgen", "configured_carver")


class WorldgenPlacedFeatureTag(TagFile):
    """Class representing a worldgen placed feature tag."""

    scope = ("tags", "worldgen", "placed_feature")
