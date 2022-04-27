"""Autoload default plugins."""


from beet import Context


def beet_default(ctx: Context):
    ctx.require(
        "beet.contrib.json_reporter",
        "beet.contrib.worldgen",
    )
