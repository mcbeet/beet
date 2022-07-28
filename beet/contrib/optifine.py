"""Plugin for supporting optifine resources."""


__all__ = [
    "optifine",
    "JsonEntityModel",
    "JsonPartModel",
    "OptifineProperties",
    "ShaderProperties",
    "OptifineTexture",
]


from typing import Union

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


class JsonEntityModel(JsonFile):
    """Class representing a json entity model."""

    scope = ("optifine", "cem")
    extension = ".jem"


class JsonPartModel(JsonFile):
    """Class representing a json part model."""

    scope = ("optifine", "cem")
    extension = ".jpm"


class OptifineProperties(TextFile):
    """Class representing optifine properties."""

    scope = ("optifine",)
    extension = ".properties"


class OptifineTexture(PngFile):
    """Class representing an optifine texture."""

    scope = ("optifine",)
    extension = ".png"


class ShaderProperties(TextFile):
    """Class representing shader properties."""

    scope = ("shaders",)
    extension = ".properties"
