"""Plugin to load unknown files."""

__all__ = [
    "UnknownAsset",
    "UnknownData",
    "unknown_files",
]


from typing import ClassVar

from beet import BinaryFile, Context, NamespaceFileScope


class UnknownAsset(BinaryFile):
    """Class representing an unknown file in resource packs."""

    scope: ClassVar[NamespaceFileScope] = ()
    extension: ClassVar[str] = ""


class UnknownData(BinaryFile):
    """Class representing an unknown file in data packs."""

    scope: ClassVar[NamespaceFileScope] = ()
    extension: ClassVar[str] = ""


def beet_default(ctx: Context):
    ctx.require(unknown_files)


def unknown_files(ctx: Context):
    """Plugin to load unknown files."""
    ctx.assets.extend_namespace.append(UnknownAsset)
    ctx.data.extend_namespace.append(UnknownData)
