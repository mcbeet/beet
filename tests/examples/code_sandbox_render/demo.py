from beet import Context, Function, sandbox
from beet.contrib.render import render


def beet_default(ctx: Context):
    ctx.data["demo:foo"] = Function(["say {{ ctx.meta.message }}"])
    ctx.require(render_functions)

    ctx.data["demo:bar"] = Function(["say {{ ctx.meta.message }}"])
    ctx.require(sandbox(add_function, render_functions))


def add_function(ctx: Context):
    ctx.data["demo:isolated"] = Function(["say isolated {{ ctx.meta.message }}"])


def render_functions(ctx: Context):
    ctx.require(render(data_pack={"functions": ["*"]}))
