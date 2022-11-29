"""Plugin that adds generated scoreboards to the data pack."""


__all__ = [
    "ScoreboardOptions",
    "scoreboard",
]


from typing import List

from beet import Context, Function, PluginOptions, configurable


class ScoreboardOptions(PluginOptions):
    function: str = "scoreboard"
    tags: List[str] = ["minecraft:load"]


def beet_default(ctx: Context):
    ctx.require(scoreboard)


@configurable(validator=ScoreboardOptions)
def scoreboard(ctx: Context, opts: ScoreboardOptions):
    """Plugin that adds generated scoreboards to the data pack."""
    if scoreboard_data := ctx.meta.get("generate_scoreboard"):
        commands = [
            f"scoreboard objectives add {name} {criterion}"
            for name, criterion in scoreboard_data.items()
        ]
        ctx.generate(opts.function, Function(commands, prepend_tags=list(opts.tags)))
        scoreboard_data.clear()
