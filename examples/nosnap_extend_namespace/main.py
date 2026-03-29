from beet import Context, BinaryFile, NamespaceFileScope
from beet.contrib.vanilla import Vanilla
from typing import ClassVar


class UnihexZip(BinaryFile):
    scope: ClassVar[NamespaceFileScope] = ()
    extension: ClassVar[str] = ".zip"


def beet_default(ctx: Context):
    vanilla = ctx.inject(Vanilla)
    vanilla.assets.extend_namespace.append(UnihexZip)
    unihex = vanilla.mount("assets/minecraft/font", fetch_objects=True).assets[
        UnihexZip
    ]
    print(unihex)
