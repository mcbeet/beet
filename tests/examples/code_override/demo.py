from beet import Context, Function


def beet_default(ctx: Context):
    ctx.require(add_function("demo:foo"))

    with ctx.override(message="world", number=9):
        ctx.require(add_function("demo:bar"))

    ctx.require(add_function("demo:after"))


def add_function(name: str):
    def plugin(ctx: Context):
        number = ctx.meta.get("number")
        message = ctx.meta.get("message")
        ctx.data[name] = Function([f"say {message=} {number=}"])

    return plugin
