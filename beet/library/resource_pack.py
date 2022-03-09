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
from typing import Any, Dict, Optional, Type

try:
    from PIL.Image import Image
except ImportError:
    Image = Any

from beet.core.file import BinaryFile, BinaryFileContent, JsonFile, PngFile, TextFile
from beet.core.utils import JsonDict, extra_field

from .base import (
    ExtraPin,
    McmetaPin,
    Namespace,
    NamespaceFile,
    NamespacePin,
    NamespaceProxyDescriptor,
    Pack,
    PackFile,
)


class Blockstate(JsonFile, NamespaceFile):
    """Class representing a blockstate."""

    scope = ("blockstates",)
    extension = ".json"


class Model(JsonFile, NamespaceFile):
    """Class representing a model."""

    scope = ("models",)
    extension = ".json"


class Language(JsonFile, NamespaceFile):
    """Class representing a language file."""

    scope = ("lang",)
    extension = ".json"

    def merge(self, other: "Language") -> bool:  # type: ignore
        self.data.update(other.data)
        return True


class Font(JsonFile, NamespaceFile):
    """Class representing a font configuration file."""

    scope = ("font",)
    extension = ".json"

    def merge(self, other: "Font") -> bool:  # type: ignore
        providers = self.data.setdefault("providers", [])

        for provider in other.data.get("providers", []):
            providers.append(deepcopy(provider))
        return True


class GlyphSizes(BinaryFile, NamespaceFile):
    """Class representing a legacy unicode glyph size file."""

    scope = ("font",)
    extension = ".bin"


class TrueTypeFont(BinaryFile, NamespaceFile):
    """Class representing a TrueType font."""

    scope = ("font",)
    extension = ".ttf"


class ShaderPost(JsonFile, NamespaceFile):
    """Class representing a shader post-processing pipeline."""

    scope = ("shaders", "post")
    extension = ".json"


class Shader(JsonFile, NamespaceFile):
    """Class representing a shader."""

    scope = ("shaders",)
    extension = ".json"


class FragmentShader(TextFile, NamespaceFile):
    """Class representing a fragment shader."""

    scope = ("shaders",)
    extension = ".fsh"


class VertexShader(TextFile, NamespaceFile):
    """Class representing a vertex shader."""

    scope = ("shaders",)
    extension = ".vsh"


class GlslShader(TextFile, NamespaceFile):
    """Class representing a glsl shader."""

    scope = ("shaders",)
    extension = ".glsl"


class Text(TextFile, NamespaceFile):
    """Class representing a text file."""

    scope = ("texts",)
    extension = ".txt"


class TextureMcmeta(JsonFile, NamespaceFile):
    """Class representing a texture mcmeta."""

    scope = ("textures",)
    extension = ".png.mcmeta"


@dataclass(eq=False, repr=False)
class Texture(PngFile, NamespaceFile):
    """Class representing a texture."""

    content: BinaryFileContent[Image] = None
    mcmeta: Optional[JsonDict] = extra_field(default=None)

    scope = ("textures",)
    extension = ".png"

    def bind(self, pack: "ResourcePack", path: str):
        super().bind(pack, path)

        if self.mcmeta is not None:
            pack.textures_mcmeta[path] = TextureMcmeta(self.mcmeta)


@dataclass(eq=False, repr=False)
class Sound(BinaryFile, NamespaceFile):
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

    scope = ("sounds",)
    extension = ".ogg"

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


class Particle(JsonFile, NamespaceFile):
    """Class representing a particle configuration file."""

    scope = ("particles",)
    extension = ".json"


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
    latest_pack_format = 8

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
