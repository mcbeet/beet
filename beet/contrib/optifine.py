"""Plugin for supporting optifine resources."""


__all__ = [
    "optifine",
    "JsonEntityModel",
    "JsonPartModel",
    "OptifineProperties",
    "ShaderProperties",
    "OptifineTexture",
]


from typing import ClassVar, Tuple, Union

from beet import Context, JsonFile, PngFile, ResourcePack, TextFile


def beet_default(ctx: Context):
    ctx.require(optifine)


def optifine(pack: Union[Context, ResourcePack]):
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


class JsonEntityModel(JsonFile[ResourcePack]):
    """Class representing a json entity model."""

    scope: ClassVar[Tuple[str, ...]] = ("optifine", "cem")
    extension: ClassVar[str] = ".jem"


class JsonPartModel(JsonFile[ResourcePack]):
    """Class representing a json part model."""

    scope: ClassVar[Tuple[str, ...]] = ("optifine", "cem")
    extension: ClassVar[str] = ".jpm"


class OptifineProperties(TextFile[ResourcePack]):
    """Class representing optifine properties."""

    scope: ClassVar[Tuple[str, ...]] = ("optifine",)
    extension: ClassVar[str] = ".properties"


class OptifineTexture(PngFile[ResourcePack]):
    """Class representing an optifine texture."""

    scope: ClassVar[Tuple[str, ...]] = ("optifine",)
    extension: ClassVar[str] = ".png"


class ShaderProperties(TextFile[ResourcePack]):
    """Class representing shader properties."""

    scope: ClassVar[Tuple[str, ...]] = ("shaders",)
    extension: ClassVar[str] = ".properties"
