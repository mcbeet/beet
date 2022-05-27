from beet import Context, Function, TextFile
from beet.contrib.clear import clear


def beet_default(ctx: Context):
    ctx.data["demo:foo"] = Function(["say foo"])
    ctx.data.extra["thing.txt"] = TextFile("thing")

    ctx.require(clear())

    ctx.data["demo:bar"] = Function(["say bar"])
