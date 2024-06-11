from beet import Context, Function, sandbox


def beet_default(ctx: Context):
    ctx.require(add_function("demo:foo"))
    ctx.require(add_function("demo:bar"))
    ctx.require(sandbox(add_function("demo:isolated")))
    ctx.require(sandbox(add_function("demo:inner1"), add_function("demo:inner2")))
    ctx.require(add_function("demo:after"))


def add_function(name: str):
    def plugin(ctx: Context):
        function_count = len(ctx.data.function)
        last_function = ctx.meta.get("last_function")
        ctx.data[name] = Function([f"say {function_count=} {last_function=}"])
        ctx.meta["last_function"] = name

    return plugin
