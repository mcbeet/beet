"""Plugin that minifies json files."""


import json

from beet import Context
from beet.contrib.format_json import format_json


def beet_default(ctx: Context):
    ctx.require(format_json(lambda content: json.dumps(content, separators=(",", ":"))))
