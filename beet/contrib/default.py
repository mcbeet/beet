"""Autoload default plugins."""


from beet import Context


def beet_default(ctx: Context):
    ctx.require("beet.contrib.worldgen")
