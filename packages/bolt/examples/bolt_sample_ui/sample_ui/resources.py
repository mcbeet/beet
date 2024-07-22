from typing import ClassVar

from beet import Context, NamespaceFileScope, TextFileBase


class UiScreen(TextFileBase[str]):
    scope: ClassVar[NamespaceFileScope] = ("ui_screens",)
    extension: ClassVar[str] = ".xml"


def beet_default(ctx: Context):
    ctx.data.extend_namespace.append(UiScreen)
