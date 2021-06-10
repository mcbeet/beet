"""Plugin that minifies json files."""


import json
from typing import Any

from beet import Context, JsonFileBase


def beet_default(ctx: Context):
    for pack in ctx.packs:
        for _, json_file in pack.list_files(extend=JsonFileBase[Any]):
            json_file.text = json.dumps(json_file.data, separators=(",", ":"))
