__all__ = [
    "ResourcePack",
    "ResourcePackNamespace",
    "Blockstate",
    "Model",
    "Language",
    "Font",
    "GlyphSizeFile",
    "TrueTypeFont",
    "ShaderPost",
    "Shader",
    "FragmentShader",
    "VertexShader",
    "GlslShader",
    "Text",
    "TextureMcmeta",
    "Texture",
]


from copy import deepcopy
from dataclasses import dataclass
from typing import Dict, Optional

from PIL import Image as img

from beet.core.file import BinaryFile, BinaryFileContent, JsonFile, PngFile, TextFile
from beet.core.utils import JsonDict, extra_field

from .base import (
    McmetaPin,
    Namespace,
    NamespaceFile,
    NamespacePin,
    NamespaceProxyDescriptor,
    Pack,
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


class GlyphSizeFile(BinaryFile, NamespaceFile):
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


@dataclass(eq=False)
class Texture(PngFile, NamespaceFile):
    """Class representing a texture."""

    content: BinaryFileContent[img.Image] = None
    mcmeta: Optional[JsonDict] = extra_field(default=None)

    scope = ("textures",)
    extension = ".png"

    def bind(self, pack: "ResourcePack", namespace: str, path: str):
        super().bind(pack, namespace, path)

        if self.mcmeta is not None:
            pack.textures_mcmeta[f"{namespace}:{path}"] = TextureMcmeta(self.mcmeta)


class ResourcePackNamespace(Namespace):
    """Class representing a resource pack namespace."""

    directory = "assets"

    # fmt: off
    blockstates:      NamespacePin[Blockstate]     = NamespacePin(Blockstate)
    models:           NamespacePin[Model]          = NamespacePin(Model)
    languages:        NamespacePin[Language]       = NamespacePin(Language)
    fonts:            NamespacePin[Font]           = NamespacePin(Font)
    glyph_sizes:      NamespacePin[GlyphSizeFile]  = NamespacePin(GlyphSizeFile)
    truetype_fonts:   NamespacePin[TrueTypeFont]   = NamespacePin(TrueTypeFont)
    shader_posts:     NamespacePin[ShaderPost]     = NamespacePin(ShaderPost)
    shaders:          NamespacePin[Shader]         = NamespacePin(Shader)
    fragment_shaders: NamespacePin[FragmentShader] = NamespacePin(FragmentShader)
    vertex_shaders:   NamespacePin[VertexShader]   = NamespacePin(VertexShader)
    glsl_shaders:     NamespacePin[GlslShader]     = NamespacePin(GlslShader)
    texts:            NamespacePin[Text]           = NamespacePin(Text)
    textures_mcmeta:  NamespacePin[TextureMcmeta]  = NamespacePin(TextureMcmeta)
    textures:         NamespacePin[Texture]        = NamespacePin(Texture)
    # fmt: on


class ResourcePack(Pack[ResourcePackNamespace]):
    """Class representing a resource pack."""

    default_name = "untitled_resource_pack"
    latest_pack_format = 6

    language_config: McmetaPin[Dict[str, JsonDict]] = McmetaPin(
        "language", default_factory=dict
    )

    # fmt: off
    blockstates:      NamespaceProxyDescriptor[Blockstate]     = NamespaceProxyDescriptor(Blockstate)
    models:           NamespaceProxyDescriptor[Model]          = NamespaceProxyDescriptor(Model)
    languages:        NamespaceProxyDescriptor[Language]       = NamespaceProxyDescriptor(Language)
    fonts:            NamespaceProxyDescriptor[Font]           = NamespaceProxyDescriptor(Font)
    glyph_sizes:      NamespaceProxyDescriptor[GlyphSizeFile]  = NamespaceProxyDescriptor(GlyphSizeFile)
    truetype_fonts:   NamespaceProxyDescriptor[TrueTypeFont]   = NamespaceProxyDescriptor(TrueTypeFont)
    shader_posts:     NamespaceProxyDescriptor[ShaderPost]     = NamespaceProxyDescriptor(ShaderPost)
    shaders:          NamespaceProxyDescriptor[Shader]         = NamespaceProxyDescriptor(Shader)
    fragment_shaders: NamespaceProxyDescriptor[FragmentShader] = NamespaceProxyDescriptor(FragmentShader)
    vertex_shaders:   NamespaceProxyDescriptor[VertexShader]   = NamespaceProxyDescriptor(VertexShader)
    glsl_shaders:     NamespaceProxyDescriptor[GlslShader]     = NamespaceProxyDescriptor(GlslShader)
    texts:            NamespaceProxyDescriptor[Text]           = NamespaceProxyDescriptor(Text)
    textures_mcmeta:  NamespaceProxyDescriptor[TextureMcmeta]  = NamespaceProxyDescriptor(TextureMcmeta)
    textures:         NamespaceProxyDescriptor[Texture]        = NamespaceProxyDescriptor(Texture)
    # fmt: on
