__all__ = [
    "Directive",
    "NamespacedResourceDirective",
    "DataPackDirective",
    "ResourcePackDirective",
    "BundleFragmentMixin",
    "RequireDirective",
    "SkipDirective",
    "get_builtin_directives",
]


import io
from dataclasses import dataclass
from typing import Any, Dict, Protocol, Type, Union
from zipfile import ZipFile

from beet import Context, DataPack, ResourcePack
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
    ItemModifier,
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
    GlslShader,
    GlyphSizeFile,
    Language,
    Model,
    Shader,
    ShaderPost,
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
        file_instance: Any = fragment.as_file(self.file_type)

        pack = assets if self.file_type in assets.namespace_type.field_map else data
        proxy: Any = pack[self.file_type]  # type: ignore

        if fragment.modifier == "append":
            current_file = proxy.setdefault(full_name, self.file_type(""))
            current_file.text += file_instance.text
        elif fragment.modifier == "merge":
            proxy.merge({full_name: file_instance})
        else:
            proxy[full_name] = file_instance


class BundleFragmentMixin:
    """Directive mixin that can bundle a fragment into a zipfile."""

    def bundle_pack_fragment(self, fragment: Fragment) -> ZipFile:
        """Return a zipfile containing the pack fragment."""
        relative_path = fragment.expect("relative_path")
        file_instance = fragment.as_file()

        data = io.BytesIO()
        with ZipFile(data, mode="w") as zip_file:
            file_instance.dump(zip_file, relative_path)

        data.seek(0)
        return ZipFile(data)


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


@dataclass
class RequireDirective:
    """Directive that requires a given plugin."""

    ctx: Context

    def __call__(self, fragment: Fragment, assets: ResourcePack, data: DataPack):
        self.ctx.require(fragment.expect("plugin"))


@dataclass
class SkipDirective:
    """Directive that ignores the fragment and skips to the next one."""

    def __call__(self, fragment: Fragment, assets: ResourcePack, data: DataPack):
        fragment.expect()


def get_builtin_directives() -> Dict[
    str,
    Union[
        NamespacedResourceDirective,
        DataPackDirective,
        ResourcePackDirective,
        SkipDirective,
    ],
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
        "item_modifier":                NamespacedResourceDirective(ItemModifier),

        "blockstate":      NamespacedResourceDirective(Blockstate),
        "model":           NamespacedResourceDirective(Model),
        "language":        NamespacedResourceDirective(Language),
        "font":            NamespacedResourceDirective(Font),
        "glyph_sizes":     NamespacedResourceDirective(GlyphSizeFile),
        "truetype_font":   NamespacedResourceDirective(TrueTypeFont),
        "shader_post":     NamespacedResourceDirective(ShaderPost),
        "shader":          NamespacedResourceDirective(Shader),
        "fragment_shader": NamespacedResourceDirective(FragmentShader),
        "vertex_shader":   NamespacedResourceDirective(VertexShader),
        "glsl_shader":     NamespacedResourceDirective(GlslShader),
        "text":            NamespacedResourceDirective(Text),
        "texture_mcmeta":  NamespacedResourceDirective(TextureMcmeta),
        "texture":         NamespacedResourceDirective(Texture),

        "data_pack":     DataPackDirective(),
        "resource_pack": ResourcePackDirective(),

        "skip": SkipDirective(),
        # fmt: on
    }
