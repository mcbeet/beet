"""Plugin that minifies json files."""


from beet import Context
from beet.contrib.format_json import format_json


def beet_default(ctx: Context):
    ctx.require(format_json(indent=None, separators=(",", ":"), final_newline=False))
