from beet import Context, DataPack
from beet.core.utils import resolve_packageable_path

from mecha import AdditionalCompilationUnitProvider, Mecha


def beet_default(ctx: Context):
    mc = ctx.inject(Mecha)
    mc.providers.append(
        AdditionalCompilationUnitProvider(lambda: [load_mylib()], mc.providers)
    )


def load_mylib() -> DataPack:
    mylib = DataPack()
    mylib.mount("data/mylib/functions", resolve_packageable_path("@mylib/functions"))
    return mylib
