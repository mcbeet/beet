from typing import ClassVar

from beet import Context, NamespaceFileScope, TextFile
from mecha import FileTypeCompilationUnitProvider, Mecha


class Custom(TextFile):
    scope: ClassVar[NamespaceFileScope] = ("custom",)
    extension: ClassVar[str] = ".bolt"


def beet_default(ctx: Context):
    ctx.data.extend_namespace.append(Custom)

    ctx.require("bolt")

    mc = ctx.inject(Mecha)
    mc.providers = [FileTypeCompilationUnitProvider([Custom])]


def remove_custom_modules(ctx: Context):
    for pack in [ctx.data, *ctx.data.overlays.values()]:
        pack[Custom].clear()
