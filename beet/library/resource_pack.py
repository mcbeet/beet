__all__ = [
    "ResourcePack",
    "ResourcePackNamespace",
    "Blockstate",
    "Model",
    "Language",
    "Font",
    "GlyphSizes",
    "TrueTypeFont",
    "ShaderPost",
    "Shader",
    "FragmentShader",
    "VertexShader",
    "GlslShader",
    "Text",
    "TextureMcmeta",
    "Texture",
    "Sound",
    "SoundConfig",
    "Particle",
]


from copy import deepcopy
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional, Tuple, Type

try:
    from PIL.Image import Image
except ImportError:
    Image = Any

from beet.core.file import BinaryFile, BinaryFileContent, JsonFile, PngFile, TextFile
from beet.core.utils import JsonDict, extra_field, split_version

from .base import (
    LATEST_MINECRAFT_VERSION,
    ExtraPin,
    McmetaPin,
    Namespace,
    NamespacePin,
    NamespaceProxyDescriptor,
    Pack,
    PackFile,
)


class Blockstate(JsonFile):
    """Class representing a blockstate."""

    scope: ClassVar[Tuple[str, ...]] = ("blockstates",)
    extension: ClassVar[str] = ".json"


class Model(JsonFile):
    """Class representing a model."""

    scope: ClassVar[Tuple[str, ...]] = ("models",)
    extension: ClassVar[str] = ".json"


class Language(JsonFile):
    """Class representing a language file."""

    scope: ClassVar[Tuple[str, ...]] = ("lang",)
    extension: ClassVar[str] = ".json"

    def merge(self, other: "Language") -> bool:  # type: ignore
        self.data.update(other.data)
        return True


class Font(JsonFile):
    """Class representing a font configuration file."""

    scope: ClassVar[Tuple[str, ...]] = ("font",)
    extension: ClassVar[str] = ".json"

    def merge(self, other: "Font") -> bool:  # type: ignore
        providers = self.data.setdefault("providers", [])

        for provider in other.data.get("providers", []):
            providers.append(deepcopy(provider))
        return True


class GlyphSizes(BinaryFile):
    """Class representing a legacy unicode glyph size file."""

    scope: ClassVar[Tuple[str, ...]] = ("font",)
    extension: ClassVar[str] = ".bin"


class TrueTypeFont(BinaryFile):
    """Class representing a TrueType font."""

    scope: ClassVar[Tuple[str, ...]] = ("font",)
    extension: ClassVar[str] = ".ttf"


class ShaderPost(JsonFile):
    """Class representing a shader post-processing pipeline."""

    scope: ClassVar[Tuple[str, ...]] = ("shaders", "post")
    extension: ClassVar[str] = ".json"


class Shader(JsonFile):
    """Class representing a shader."""

    scope: ClassVar[Tuple[str, ...]] = ("shaders",)
    extension: ClassVar[str] = ".json"


class FragmentShader(TextFile):
    """Class representing a fragment shader."""

    scope: ClassVar[Tuple[str, ...]] = ("shaders",)
    extension: ClassVar[str] = ".fsh"


class VertexShader(TextFile):
    """Class representing a vertex shader."""

    scope: ClassVar[Tuple[str, ...]] = ("shaders",)
    extension: ClassVar[str] = ".vsh"


class GlslShader(TextFile):
    """Class representing a glsl shader."""

    scope: ClassVar[Tuple[str, ...]] = ("shaders",)
    extension: ClassVar[str] = ".glsl"


class Text(TextFile):
    """Class representing a text file."""

    scope: ClassVar[Tuple[str, ...]] = ("texts",)
    extension: ClassVar[str] = ".txt"


class TextureMcmeta(JsonFile):
    """Class representing a texture mcmeta."""

    scope: ClassVar[Tuple[str, ...]] = ("textures",)
    extension: ClassVar[str] = ".png.mcmeta"


@dataclass(eq=False, repr=False)
class Texture(PngFile):
    """Class representing a texture."""

    content: BinaryFileContent[Image] = None
    mcmeta: Optional[JsonDict] = extra_field(default=None)

    scope: ClassVar[Tuple[str, ...]] = ("textures",)
    extension: ClassVar[str] = ".png"

    def bind(self, pack: "ResourcePack", path: str):
        super().bind(pack, path)

        if self.mcmeta is not None:
            pack.textures_mcmeta[path] = TextureMcmeta(self.mcmeta)


@dataclass(eq=False, repr=False)
class Sound(BinaryFile):
    """Class representing a sound file."""

    event: Optional[str] = extra_field(default=None)
    subtitle: Optional[str] = extra_field(default=None)
    replace: Optional[bool] = extra_field(default=None)
    volume: Optional[float] = extra_field(default=None)
    pitch: Optional[float] = extra_field(default=None)
    weight: Optional[int] = extra_field(default=None)
    stream: Optional[bool] = extra_field(default=None)
    attenuation_distance: Optional[int] = extra_field(default=None)
    preload: Optional[bool] = extra_field(default=None)

    scope: ClassVar[Tuple[str, ...]] = ("sounds",)
    extension: ClassVar[str] = ".ogg"

    def bind(self, pack: "ResourcePack", path: str):
        super().bind(pack, path)

        namespace, _, path = path.partition(":")

        if self.event is not None:
            attributes = {
                "volume": self.volume,
                "pitch": self.pitch,
                "weight": self.weight,
                "stream": self.stream,
                "attenuation_distance": self.attenuation_distance,
                "preload": self.preload,
            }

            attributes = {k: v for k, v in attributes.items() if v is not None}
            event: JsonDict = {
                "sounds": [{"name": path, **attributes} if attributes else path]
            }

            if self.replace is not None:
                event["replace"] = self.replace
            if self.subtitle is not None:
                event["subtitle"] = self.subtitle

            pack[namespace].extra.merge(
                {"sounds.json": SoundConfig({self.event: event})}
            )


class SoundConfig(JsonFile):
    """Class representing the sounds.json configuration."""

    def merge(self, other: "SoundConfig") -> bool:  # type: ignore
        for key, other_event in other.data.items():
            if other_event.get("replace"):
                self.data[key] = deepcopy(other_event)
                continue

            event = self.data.setdefault(key, {})

            if subtitle := other_event.get("subtitle"):
                event["subtitle"] = subtitle

            sounds = event.setdefault("sounds", [])
            for sound in other_event.get("sounds", []):
                if sound not in sounds:
                    sounds.append(deepcopy(sound))

        return True


class Particle(JsonFile):
    """Class representing a particle configuration file."""

    scope: ClassVar[Tuple[str, ...]] = ("particles",)
    extension: ClassVar[str] = ".json"


class ResourcePackNamespace(Namespace):
    """Class representing a resource pack namespace."""

    directory = "assets"

    sound_config: ExtraPin[Optional[SoundConfig]] = ExtraPin(
        "sounds.json", default=None
    )

    # fmt: off
    blockstates:      NamespacePin[Blockstate]     = NamespacePin(Blockstate)
    models:           NamespacePin[Model]          = NamespacePin(Model)
    languages:        NamespacePin[Language]       = NamespacePin(Language)
    fonts:            NamespacePin[Font]           = NamespacePin(Font)
    glyph_sizes:      NamespacePin[GlyphSizes]     = NamespacePin(GlyphSizes)
    true_type_fonts:  NamespacePin[TrueTypeFont]   = NamespacePin(TrueTypeFont)
    shader_posts:     NamespacePin[ShaderPost]     = NamespacePin(ShaderPost)
    shaders:          NamespacePin[Shader]         = NamespacePin(Shader)
    fragment_shaders: NamespacePin[FragmentShader] = NamespacePin(FragmentShader)
    vertex_shaders:   NamespacePin[VertexShader]   = NamespacePin(VertexShader)
    glsl_shaders:     NamespacePin[GlslShader]     = NamespacePin(GlslShader)
    texts:            NamespacePin[Text]           = NamespacePin(Text)
    textures_mcmeta:  NamespacePin[TextureMcmeta]  = NamespacePin(TextureMcmeta)
    textures:         NamespacePin[Texture]        = NamespacePin(Texture)
    sounds:           NamespacePin[Sound]          = NamespacePin(Sound)
    particles:        NamespacePin[Particle]       = NamespacePin(Particle)
    # fmt: on

    @classmethod
    def get_extra_info(cls) -> Dict[str, Type[PackFile]]:
        return {**super().get_extra_info(), "sounds.json": SoundConfig}


class ResourcePack(Pack[ResourcePackNamespace]):
    """Class representing a resource pack."""

    default_name = "untitled_resource_pack"

    pack_format_registry = {
        (1, 6): 1,
        (1, 7): 1,
        (1, 8): 1,
        (1, 9): 2,
        (1, 10): 2,
        (1, 11): 3,
        (1, 12): 3,
        (1, 13): 4,
        (1, 14): 4,
        (1, 15): 5,
        (1, 16): 6,
        (1, 17): 7,
        (1, 18): 8,
        (1, 19): 9,
    }
    latest_pack_format = pack_format_registry[split_version(LATEST_MINECRAFT_VERSION)]

    language_config = McmetaPin[Dict[str, JsonDict]]("language", default_factory=dict)

    # fmt: off
    blockstates:      NamespaceProxyDescriptor[Blockstate]     = NamespaceProxyDescriptor(Blockstate)
    models:           NamespaceProxyDescriptor[Model]          = NamespaceProxyDescriptor(Model)
    languages:        NamespaceProxyDescriptor[Language]       = NamespaceProxyDescriptor(Language)
    fonts:            NamespaceProxyDescriptor[Font]           = NamespaceProxyDescriptor(Font)
    glyph_sizes:      NamespaceProxyDescriptor[GlyphSizes]     = NamespaceProxyDescriptor(GlyphSizes)
    true_type_fonts:  NamespaceProxyDescriptor[TrueTypeFont]   = NamespaceProxyDescriptor(TrueTypeFont)
    shader_posts:     NamespaceProxyDescriptor[ShaderPost]     = NamespaceProxyDescriptor(ShaderPost)
    shaders:          NamespaceProxyDescriptor[Shader]         = NamespaceProxyDescriptor(Shader)
    fragment_shaders: NamespaceProxyDescriptor[FragmentShader] = NamespaceProxyDescriptor(FragmentShader)
    vertex_shaders:   NamespaceProxyDescriptor[VertexShader]   = NamespaceProxyDescriptor(VertexShader)
    glsl_shaders:     NamespaceProxyDescriptor[GlslShader]     = NamespaceProxyDescriptor(GlslShader)
    texts:            NamespaceProxyDescriptor[Text]           = NamespaceProxyDescriptor(Text)
    textures_mcmeta:  NamespaceProxyDescriptor[TextureMcmeta]  = NamespaceProxyDescriptor(TextureMcmeta)
    textures:         NamespaceProxyDescriptor[Texture]        = NamespaceProxyDescriptor(Texture)
    sounds:           NamespaceProxyDescriptor[Sound]          = NamespaceProxyDescriptor(Sound)
    particles:        NamespaceProxyDescriptor[Particle]       = NamespaceProxyDescriptor(Particle)
    # fmt: on
