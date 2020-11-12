__all__ = [
    "ResourcePack",
    "ResourcePackNamespace",
    "Blockstate",
    "Model",
    "Texture",
    "Text",
]


from dataclasses import dataclass, field

from .file import JsonFile, PlainTextFile, PngFile
from .pack import FileContainer, FileContainerProxyDescriptor, Namespace, Pack


@dataclass
class Blockstate(JsonFile):
    path = ("blockstates",)


@dataclass
class Model(JsonFile):
    path = ("models",)


@dataclass
class Texture(PngFile):
    path = ("textures",)


@dataclass
class Text(PlainTextFile):
    path = ("texts",)


@dataclass
class ResourcePackNamespace(Namespace):
    # fmt: off
    blockstates: FileContainer[Blockstate] = field(default_factory=FileContainer)
    models: FileContainer[Model] = field(default_factory=FileContainer)
    textures: FileContainer[Texture] = field(default_factory=FileContainer)
    texts: FileContainer[Text] = field(default_factory=FileContainer)
    # fmt: on

    directory = "assets"


@dataclass
class ResourcePack(Pack[ResourcePackNamespace]):
    # fmt: off
    blockstates = FileContainerProxyDescriptor[Blockstate]()
    models = FileContainerProxyDescriptor[Model]()
    textures = FileContainerProxyDescriptor[Texture]()
    texts = FileContainerProxyDescriptor[Text]()
    # fmt: on

    latest_pack_format = 6
