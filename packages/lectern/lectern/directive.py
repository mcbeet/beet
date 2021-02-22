__all__ = [
    "Directive",
    "NamespacedResourceDirective",
    "DataPackDirective",
    "ResourcePackDirective",
    "BundleFragmentMixin",
    "get_builtin_directives",
]


import io
from dataclasses import dataclass
from typing import Dict, Protocol, Type, Union
from zipfile import ZipFile

from beet import DataPack, ResourcePack
from beet.library.base import NamespaceFile
from beet.library.data_pack import (
    Advancement,
    Biome,
    BlockTag,
    ConfiguredCarver,
    ConfiguredFeature,
    ConfiguredStructureFeature,
    ConfiguredSurfaceBuilder,
    Dimension,
    DimensionType,
    EntityTypeTag,
    FluidTag,
    Function,
    FunctionTag,
    ItemTag,
    LootTable,
    NoiseSettings,
    Predicate,
    ProcessorList,
    Recipe,
    Structure,
    TemplatePool,
)
from beet.library.resource_pack import (
    Blockstate,
    Font,
    FragmentShader,
    GlyphSizeFile,
    Model,
    ShaderPost,
    ShaderProgram,
    Text,
    Texture,
    TextureMcmeta,
    TrueTypeFont,
    VertexShader,
)

from .fragment import Fragment


class Directive(Protocol):
    """Protocol for detecting directives."""

    def __call__(self, fragment: Fragment, assets: ResourcePack, data: DataPack):
        ...


@dataclass
class NamespacedResourceDirective:
    """Directive for including namespaced resources."""

    file_type: Type[NamespaceFile]

    def __call__(self, fragment: Fragment, assets: ResourcePack, data: DataPack):
        full_name = fragment.expect("full_name")
        content = fragment.apply_modifier()

        file_instance = self.file_type(content)

        if self.file_type in assets.namespace_type.field_map:
            assets[full_name] = file_instance
        else:
            data[full_name] = file_instance


class BundleFragmentMixin:
    """Directive mixin that can bundle a fragment into a zipfile."""

    def bundle_pack_fragment(self, fragment: Fragment) -> ZipFile:
        """Return a zipfile containing the pack fragment."""
        relative_path = fragment.expect("relative_path")
        content = fragment.apply_modifier()

        data = io.BytesIO()
        with ZipFile(data, mode="w") as zip_file:
            zip_file.writestr(relative_path, content)

        return ZipFile(io.BytesIO(data.getvalue()))


@dataclass
class DataPackDirective(BundleFragmentMixin):
    """Directive that loads the fragment into the data pack."""

    def __call__(self, fragment: Fragment, assets: ResourcePack, data: DataPack):
        data.load(self.bundle_pack_fragment(fragment))


@dataclass
class ResourcePackDirective(BundleFragmentMixin):
    """Directive that loads the fragment into the resource pack."""

    def __call__(self, fragment: Fragment, assets: ResourcePack, data: DataPack):
        assets.load(self.bundle_pack_fragment(fragment))


def get_builtin_directives() -> Dict[
    str, Union[NamespacedResourceDirective, DataPackDirective, ResourcePackDirective]
]:
    """Return the built-in directives."""
    return {
        # fmt: off
        "advancement":                  NamespacedResourceDirective(Advancement),
        "function":                     NamespacedResourceDirective(Function),
        "loot_table":                   NamespacedResourceDirective(LootTable),
        "predicate":                    NamespacedResourceDirective(Predicate),
        "recipe":                       NamespacedResourceDirective(Recipe),
        "structure":                    NamespacedResourceDirective(Structure),
        "block_tag":                    NamespacedResourceDirective(BlockTag),
        "entity_type_tag":              NamespacedResourceDirective(EntityTypeTag),
        "fluid_tag":                    NamespacedResourceDirective(FluidTag),
        "function_tag":                 NamespacedResourceDirective(FunctionTag),
        "item_tag":                     NamespacedResourceDirective(ItemTag),
        "dimension_type":               NamespacedResourceDirective(DimensionType),
        "dimension":                    NamespacedResourceDirective(Dimension),
        "biome":                        NamespacedResourceDirective(Biome),
        "configured_carver":            NamespacedResourceDirective(ConfiguredCarver),
        "configured_feature":           NamespacedResourceDirective(ConfiguredFeature),
        "configured_structure_feature": NamespacedResourceDirective(ConfiguredStructureFeature),
        "configured_surface_builder":   NamespacedResourceDirective(ConfiguredSurfaceBuilder),
        "noise_settings":               NamespacedResourceDirective(NoiseSettings),
        "processor_list":               NamespacedResourceDirective(ProcessorList),
        "template_pool":                NamespacedResourceDirective(TemplatePool),

        "blockstate":      NamespacedResourceDirective(Blockstate),
        "model":           NamespacedResourceDirective(Model),
        "font":            NamespacedResourceDirective(Font),
        "glyph_sizes":     NamespacedResourceDirective(GlyphSizeFile),
        "truetype_font":   NamespacedResourceDirective(TrueTypeFont),
        "shader_post":     NamespacedResourceDirective(ShaderPost),
        "shader_program":  NamespacedResourceDirective(ShaderProgram),
        "fragment_shader": NamespacedResourceDirective(FragmentShader),
        "vertex_shader":   NamespacedResourceDirective(VertexShader),
        "text":            NamespacedResourceDirective(Text),
        "texture_mcmeta":  NamespacedResourceDirective(TextureMcmeta),
        "texture":         NamespacedResourceDirective(Texture),

        "data_pack":     DataPackDirective(),
        "resource_pack": ResourcePackDirective(),
        # fmt: on
    }
