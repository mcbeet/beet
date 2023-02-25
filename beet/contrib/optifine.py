"""Plugin for supporting optifine resources."""


__all__ = [
    "optifine",
    "JsonEntityModel",
    "JsonPartModel",
    "OptifineProperties",
    "ShaderProperties",
    "OptifineTexture",
]


from typing import ClassVar

from beet import Context, JsonFileBase, PngFileBase, RawTextFileBase, ResourcePack
from beet.core.utils import JsonDict


def beet_default(ctx: Context):
    ctx.require(optifine)


def optifine(pack: Context | ResourcePack):
    """Enable optifine resources."""
    if isinstance(pack, Context):
        pack = pack.assets

    pack.extend_namespace += [
        JsonEntityModel,
        JsonPartModel,
        OptifineProperties,
        ShaderProperties,
        OptifineTexture,
    ]


class JsonEntityModel(JsonFileBase[JsonDict]):
    """Class representing a json entity model."""

    scope: ClassVar[tuple[str, ...]] = ("optifine", "cem")
    extension: ClassVar[str] = ".jem"


class JsonPartModel(JsonFileBase[JsonDict]):
    """Class representing a json part model."""

    scope: ClassVar[tuple[str, ...]] = ("optifine", "cem")
    extension: ClassVar[str] = ".jpm"


class OptifineProperties(RawTextFileBase):
    """Class representing optifine properties."""

    scope: ClassVar[tuple[str, ...]] = ("optifine",)
    extension: ClassVar[str] = ".properties"


class OptifineTexture(PngFileBase):
    """Class representing an optifine texture."""

    scope: ClassVar[tuple[str, ...]] = ("optifine",)
    extension: ClassVar[str] = ".png"


class ShaderProperties(RawTextFileBase):
    """Class representing shader properties."""

    scope: ClassVar[tuple[str, ...]] = ("shaders",)
    extension: ClassVar[str] = ".properties"
