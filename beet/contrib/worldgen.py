"""Plugin for experimental worldgen."""

__all__ = [
    "worldgen",
    "Dimension",
    "DimensionType",
    "WorldgenBiome",
    "WorldgenConfiguredCarver",
    "WorldgenConfiguredFeature",
    "WorldgenDensityFunction",
    "WorldgenNoise",
    "WorldgenNoiseSettings",
    "WorldgenPlacedFeature",
    "WorldgenProcessorList",
    "WorldgenStructure",
    "WorldgenStructureSet",
    "WorldgenConfiguredSurfaceBuilder",
    "WorldgenTemplatePool",
    "WorldgenWorldPreset",
    "WorldgenFlatLevelGeneratorPreset",
    "WorldgenBiomeTag",
    "WorldgenStructureSetTag",
    "WorldgenStructureTag",
    "WorldgenConfiguredCarverTag",
    "WorldgenPlacedFeatureTag",
]


from typing import ClassVar, Union

from beet import Context, DataPack, JsonFile, TagFile, NamespaceFileScope


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
        WorldgenDensityFunction,
        WorldgenNoise,
        WorldgenNoiseSettings,
        WorldgenPlacedFeature,
        WorldgenProcessorList,
        WorldgenStructure,
        WorldgenStructureSet,
        WorldgenConfiguredSurfaceBuilder,
        WorldgenTemplatePool,
        WorldgenWorldPreset,
        WorldgenFlatLevelGeneratorPreset,
        WorldgenBiomeTag,
        WorldgenStructureSetTag,
        WorldgenStructureTag,
        WorldgenConfiguredCarverTag,
        WorldgenPlacedFeatureTag,
    ]


class Dimension(JsonFile):
    """Class representing a dimension."""

    scope: ClassVar[NamespaceFileScope] = ("dimension",)
    extension: ClassVar[str] = ".json"


class DimensionType(JsonFile):
    """Class representing a dimension type."""

    scope: ClassVar[NamespaceFileScope] = ("dimension_type",)
    extension: ClassVar[str] = ".json"


class WorldgenBiome(JsonFile):
    """Class representing a biome."""

    scope: ClassVar[NamespaceFileScope] = ("worldgen", "biome")
    extension: ClassVar[str] = ".json"


class WorldgenConfiguredCarver(JsonFile):
    """Class representing a worldgen carver."""

    scope: ClassVar[NamespaceFileScope] = ("worldgen", "configured_carver")
    extension: ClassVar[str] = ".json"


class WorldgenConfiguredFeature(JsonFile):
    """Class representing a worldgen feature."""

    scope: ClassVar[NamespaceFileScope] = ("worldgen", "configured_feature")
    extension: ClassVar[str] = ".json"


class WorldgenDensityFunction(JsonFile):
    """Class representing a density function."""

    scope: ClassVar[NamespaceFileScope] = ("worldgen", "density_function")
    extension: ClassVar[str] = ".json"


class WorldgenNoise(JsonFile):
    """Class representing a worldgen noise."""

    scope: ClassVar[NamespaceFileScope] = ("worldgen", "noise")
    extension: ClassVar[str] = ".json"


class WorldgenNoiseSettings(JsonFile):
    """Class representing worldgen noise settings."""

    scope: ClassVar[NamespaceFileScope] = ("worldgen", "noise_settings")
    extension: ClassVar[str] = ".json"


class WorldgenPlacedFeature(JsonFile):
    """Class representing a placed feature."""

    scope: ClassVar[NamespaceFileScope] = ("worldgen", "placed_feature")
    extension: ClassVar[str] = ".json"


class WorldgenProcessorList(JsonFile):
    """Class representing a worldgen processor list."""

    scope: ClassVar[NamespaceFileScope] = ("worldgen", "processor_list")
    extension: ClassVar[str] = ".json"


class WorldgenStructure(JsonFile):
    """Class representing a worldgen structure feature."""

    scope: ClassVar[NamespaceFileScope] = ("worldgen", "structure")
    extension: ClassVar[str] = ".json"


class WorldgenStructureSet(JsonFile):
    """Class representing a worldgen structure set."""

    scope: ClassVar[NamespaceFileScope] = ("worldgen", "structure_set")
    extension: ClassVar[str] = ".json"


class WorldgenConfiguredSurfaceBuilder(JsonFile):
    """Class representing a worldgen surface builder."""

    scope: ClassVar[NamespaceFileScope] = ("worldgen", "configured_surface_builder")
    extension: ClassVar[str] = ".json"


class WorldgenTemplatePool(JsonFile):
    """Class representing a worldgen template pool."""

    scope: ClassVar[NamespaceFileScope] = ("worldgen", "template_pool")
    extension: ClassVar[str] = ".json"


class WorldgenWorldPreset(JsonFile):
    """Class representing a worldgen world preset."""

    scope: ClassVar[NamespaceFileScope] = ("worldgen", "world_preset")
    extension: ClassVar[str] = ".json"


class WorldgenFlatLevelGeneratorPreset(JsonFile):
    """Class representing a worldgen flat level generator preset."""

    scope: ClassVar[NamespaceFileScope] = ("worldgen", "flat_level_generator_preset")
    extension: ClassVar[str] = ".json"


class WorldgenBiomeTag(TagFile):
    """Class representing a biome tag."""

    scope: ClassVar[NamespaceFileScope] = ("tags", "worldgen", "biome")


class WorldgenStructureTag(TagFile):
    """Class representing a worldgen structure feature tag."""

    scope: ClassVar[NamespaceFileScope] = ("tags", "worldgen", "structure")


class WorldgenStructureSetTag(TagFile):
    """Class representing a worldgen structure set tag."""

    scope: ClassVar[NamespaceFileScope] = ("tags", "worldgen", "structure_set")


class WorldgenConfiguredCarverTag(TagFile):
    """Class representing a worldgen carver tag."""

    scope: ClassVar[NamespaceFileScope] = ("tags", "worldgen", "configured_carver")


class WorldgenPlacedFeatureTag(TagFile):
    """Class representing a worldgen placed feature tag."""

    scope: ClassVar[NamespaceFileScope] = ("tags", "worldgen", "placed_feature")
