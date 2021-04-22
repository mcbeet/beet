"""Plugin that adds generated scoreboards to the data pack."""


__all__ = [
    "scoreboard",
]


from typing import Iterable, cast

from beet import Context, Function, Plugin
from beet.core.utils import JsonDict


def beet_default(ctx: Context):
    config = ctx.meta.get("scoreboard", cast(JsonDict, {}))

    function = config.get("function", "scoreboard")
    tags = config.get("tags", ["minecraft:load"])

    ctx.require(scoreboard(function, tags))


def scoreboard(
    function: str = "scoreboard",
    tags: Iterable[str] = ("minecraft:load",),
) -> Plugin:
    """Return a plugin that adds generated scoreboards to the data pack."""

    def plugin(ctx: Context):
        if scoreboard_data := ctx.meta.get("generate_scoreboard"):
            commands = [
                f"scoreboard objectives add {name} {criterion}"
                for name, criterion in scoreboard_data.items()
            ]

            ctx.generate(function, Function(commands, prepend_tags=list(tags)))
            scoreboard_data.clear()

    return plugin
