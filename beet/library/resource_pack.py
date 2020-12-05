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

from beet.core.file import BinaryFileContent, PngFile, TextFile
from beet.core.utils import JsonDict, extra_field

from .base import (
    Namespace,
    NamespaceFile,
    NamespaceJsonFile,
    NamespacePin,
    NamespaceProxyDescriptor,
    Pack,
)


class Blockstate(NamespaceJsonFile):
    scope = ("blockstates",)


class Model(NamespaceJsonFile):
    scope = ("models",)


class TextureMcmeta(NamespaceJsonFile):
    scope = ("textures",)
    extension = ".png.mcmeta"


@dataclass(eq=False)
class Texture(PngFile, NamespaceFile):
    content: BinaryFileContent[img.Image] = None
    mcmeta: Optional[JsonDict] = extra_field(default=None)

    scope = ("textures",)
    extension = ".png"

    def bind(self, pack: "ResourcePack", namespace: str, path: str):
        if self.mcmeta:
            pack.textures_mcmeta[f"{namespace}:{path}"] = TextureMcmeta(self.mcmeta)


class Text(TextFile, NamespaceFile):
    scope = ("texts",)
    extension = ".txt"


class ResourcePackNamespace(Namespace):
    # fmt: off
    blockstates     = NamespacePin(Blockstate)
    models          = NamespacePin(Model)
    textures_mcmeta = NamespacePin(TextureMcmeta)
    textures        = NamespacePin(Texture)
    texts           = NamespacePin(Text)
    # fmt: on

    directory = "assets"


class ResourcePack(Pack[ResourcePackNamespace]):
    # fmt: off
    blockstates     = NamespaceProxyDescriptor(Blockstate)
    models          = NamespaceProxyDescriptor(Model)
    textures_mcmeta = NamespaceProxyDescriptor(TextureMcmeta)
    textures        = NamespaceProxyDescriptor(Texture)
    texts           = NamespaceProxyDescriptor(Text)
    # fmt: on

    default_name = "untitled_resource_pack"
    latest_pack_format = 6
