from beet import Context


def beet_default(ctx: Context):
    ctx.generate.objective()
    ctx.generate.objective("{hash}", "something")
    ctx.generate.objective("hello", criterion="playerKillCount")
    ctx.generate.objective("world", display="Something")

    generate = ctx.generate["foo"]["bar"]
    generate.objective()
    generate.objective("{hash}", "something")
    generate.objective("hello", criterion="playerKillCount")
    generate.objective("world", display="Something")

    ctx.generate.objective(
        "{hash}", "something", display={"text": "Update name", "color": "red"}
    )
