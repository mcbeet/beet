from beet import Context, Function
from beet.contrib.render import render


def beet_default(ctx: Context):
    ctx.data["demo:foo"] = Function(["say {{ message }}"])

    ctx.require(render(data_pack={"functions": ["*"]}))
