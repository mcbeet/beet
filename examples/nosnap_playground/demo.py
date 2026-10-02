import re

from beet import Context, Function, ErrorMessage
from beet.contrib.playground import Playground, playground_logs
from beet.contrib.singleton import singleton


def beet_default(ctx: Context):
    ctx.require("beet.contrib.playground")

    with playground_logs(timeout=0.5) as output:
        playground = ctx.inject(singleton(Playground))

        playground.run("scoreboard objectives add temp dummy")
        playground.run("scoreboard players set #value temp 29")
        playground.run("scoreboard players add #value temp 13")

        for line in output:
            if m := re.search(r"now (\d+)", line):
                ctx.generate(Function(f"say {m[1]}", tags=["minecraft:load"]))
                break
        else:
            raise ErrorMessage("Couldn't parse result from playground logs.")
