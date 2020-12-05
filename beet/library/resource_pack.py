__all__ = [
    "ResourcePack",
    "ResourcePackNamespace",
    "Blockstate",
    "Model",
    "TextureMcmeta",
    "Texture",
    "Text",
]


from dataclasses import dataclass
from typing import Optional

from PIL import Image as img

from beet.core.file import BinaryFileContent, JsonFile, PngFile, TextFile
from beet.core.utils import JsonDict, extra_field

from .base import Namespace, NamespaceFile, NamespacePin, NamespaceProxyDescriptor, Pack


class Blockstate(JsonFile, NamespaceFile):
    """Class representing a resource pack block state."""

    scope = ("blockstates",)
    extension = ".json"


class Model(JsonFile, NamespaceFile):
    """Class representing a resource pack model."""

    scope = ("models",)
    extension = ".json"


class TextureMcmeta(JsonFile, NamespaceFile):
    """Class representing a resource pack texture mcmeta."""

    scope = ("textures",)
    extension = ".png.mcmeta"


@dataclass(eq=False)
class Texture(PngFile, NamespaceFile):
    """Class representing a resource pack texture."""

    content: BinaryFileContent[img.Image] = None
    mcmeta: Optional[JsonDict] = extra_field(default=None)

    scope = ("textures",)
    extension = ".png"

    def bind(self, pack: "ResourcePack", namespace: str, path: str):
        if self.mcmeta is not None:
            pack.textures_mcmeta[f"{namespace}:{path}"] = TextureMcmeta(self.mcmeta)


class Text(TextFile, NamespaceFile):
    """Class representing a resource pack text file."""

    scope = ("texts",)
    extension = ".txt"


class ResourcePackNamespace(Namespace):
    """Class representing a resource pack namespace."""

    directory = "assets"

    # fmt: off
    blockstates     = NamespacePin(Blockstate)
    models          = NamespacePin(Model)
    textures_mcmeta = NamespacePin(TextureMcmeta)
    textures        = NamespacePin(Texture)
    texts           = NamespacePin(Text)
    # fmt: on


class ResourcePack(Pack[ResourcePackNamespace]):
    """Class representing a resource pack."""

    default_name = "untitled_resource_pack"
    latest_pack_format = 6

    # fmt: off
    blockstates     = NamespaceProxyDescriptor(Blockstate)
    models          = NamespaceProxyDescriptor(Model)
    textures_mcmeta = NamespaceProxyDescriptor(TextureMcmeta)
    textures        = NamespaceProxyDescriptor(Texture)
    texts           = NamespaceProxyDescriptor(Text)
    # fmt: on
