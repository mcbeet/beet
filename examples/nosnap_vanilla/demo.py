from beet import Context
from beet.contrib.vanilla import Vanilla


def beet_default(ctx: Context):
    vanilla = ctx.inject(Vanilla)

    assert vanilla.releases["22w11a"].type == "snapshot"

    ctx.data.merge(vanilla.mount("data/minecraft/loot_tables").data)
    ctx.data["demo"].recipes.merge(
        vanilla.mount("data/minecraft/recipes").data["minecraft"].recipes
    )
