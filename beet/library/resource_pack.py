__all__ = [
    "ResourcePack",
    "ResourcePackNamespace",
    "Blockstate",
    "Model",
    "TextureMcmeta",
    "Texture",
    "Text",
]


from dataclasses import dataclass, field
from typing import Optional

from PIL import Image as img

from beet.core.file import BinaryFileContent, PngFile, TextFile
from beet.core.utils import JsonDict, extra_field

from .base import (
    FileContainer,
    FileContainerProxyDescriptor,
    Namespace,
    NamespaceFile,
    NamespaceJsonFile,
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


@dataclass(repr=False)
class ResourcePackNamespace(Namespace):
    # fmt: off
    blockstates     : FileContainer[Blockstate]    = field(default_factory=FileContainer)
    models          : FileContainer[Model]         = field(default_factory=FileContainer)
    textures_mcmeta : FileContainer[TextureMcmeta] = field(default_factory=FileContainer)
    textures        : FileContainer[Texture]       = field(default_factory=FileContainer)
    texts           : FileContainer[Text]          = field(default_factory=FileContainer)
    # fmt: on

    directory = "assets"


class ResourcePack(Pack[ResourcePackNamespace]):
    # fmt: off
    blockstates     = FileContainerProxyDescriptor(Blockstate)
    models          = FileContainerProxyDescriptor(Model)
    textures_mcmeta = FileContainerProxyDescriptor(TextureMcmeta)
    textures        = FileContainerProxyDescriptor(Texture)
    texts           = FileContainerProxyDescriptor(Text)
    # fmt: on

    default_name = "untitled_resource_pack"
    latest_pack_format = 6
