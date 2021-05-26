from beet import Context, Function


def add_greeting(ctx: Context):
    ctx.data["greeting:hello"] = Function(["say hello"] * 5, tags=["minecraft:load"])
