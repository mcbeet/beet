__all__ = [
    "ResourcePack",
    "ResourcePackNamespace",
    "Blockstate",
    "Model",
    "Font",
    "GlyphSizeFile",
    "TrueTypeFont",
    "ShaderPost",
    "ShaderProgram",
    "FragmentShader",
    "VertexShader",
    "Text",
    "TextureMcmeta",
    "Texture",
]


from copy import deepcopy
from dataclasses import dataclass
from typing import Optional

from PIL import Image as img

from beet.core.file import BinaryFile, BinaryFileContent, JsonFile, PngFile, TextFile
from beet.core.utils import JsonDict, extra_field

from .base import Namespace, NamespaceFile, NamespacePin, NamespaceProxyDescriptor, Pack


class Blockstate(JsonFile, NamespaceFile):
    """Class representing a blockstate."""

    scope = ("blockstates",)
    extension = ".json"


class Model(JsonFile, NamespaceFile):
    """Class representing a model."""

    scope = ("models",)
    extension = ".json"


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


class ShaderProgram(JsonFile, NamespaceFile):
    """Class representing a shader program."""

    scope = ("shaders", "program")
    extension = ".json"


class FragmentShader(TextFile, NamespaceFile):
    """Class representing a fragment shader."""

    scope = ("shaders", "program")
    extension = ".fsh"


class VertexShader(TextFile, NamespaceFile):
    """Class representing a vertex shader."""

    scope = ("shaders", "program")
    extension = ".vsh"


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
    fonts:            NamespacePin[Font]           = NamespacePin(Font)
    glyph_sizes:      NamespacePin[GlyphSizeFile]  = NamespacePin(GlyphSizeFile)
    truetype_fonts:   NamespacePin[TrueTypeFont]   = NamespacePin(TrueTypeFont)
    shader_posts:     NamespacePin[ShaderPost]     = NamespacePin(ShaderPost)
    shader_programs:  NamespacePin[ShaderProgram]  = NamespacePin(ShaderProgram)
    fragment_shaders: NamespacePin[FragmentShader] = NamespacePin(FragmentShader)
    vertex_shaders:   NamespacePin[VertexShader]   = NamespacePin(VertexShader)
    texts:            NamespacePin[Text]           = NamespacePin(Text)
    textures_mcmeta:  NamespacePin[TextureMcmeta]  = NamespacePin(TextureMcmeta)
    textures:         NamespacePin[Texture]        = NamespacePin(Texture)
    # fmt: on


class ResourcePack(Pack[ResourcePackNamespace]):
    """Class representing a resource pack."""

    default_name = "untitled_resource_pack"
    latest_pack_format = 6

    # fmt: off
    blockstates:      NamespaceProxyDescriptor[Blockstate]     = NamespaceProxyDescriptor(Blockstate)
    models:           NamespaceProxyDescriptor[Model]          = NamespaceProxyDescriptor(Model)
    fonts:            NamespaceProxyDescriptor[Font]           = NamespaceProxyDescriptor(Font)
    glyph_sizes:      NamespaceProxyDescriptor[GlyphSizeFile]  = NamespaceProxyDescriptor(GlyphSizeFile)
    truetype_fonts:   NamespaceProxyDescriptor[TrueTypeFont]   = NamespaceProxyDescriptor(TrueTypeFont)
    shader_posts:     NamespaceProxyDescriptor[ShaderPost]     = NamespaceProxyDescriptor(ShaderPost)
    shader_programs:  NamespaceProxyDescriptor[ShaderProgram]  = NamespaceProxyDescriptor(ShaderProgram)
    fragment_shaders: NamespaceProxyDescriptor[FragmentShader] = NamespaceProxyDescriptor(FragmentShader)
    vertex_shaders:   NamespaceProxyDescriptor[VertexShader]   = NamespaceProxyDescriptor(VertexShader)
    texts:            NamespaceProxyDescriptor[Text]           = NamespaceProxyDescriptor(Text)
    textures_mcmeta:  NamespaceProxyDescriptor[TextureMcmeta]  = NamespaceProxyDescriptor(TextureMcmeta)
    textures:         NamespaceProxyDescriptor[Texture]        = NamespaceProxyDescriptor(Texture)
    # fmt: on
