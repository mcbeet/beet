from beet import Context
from beet.contrib.vanilla import Vanilla, load_vanilla


def beet_default(ctx: Context):
    vanilla = ctx.inject(Vanilla)

    assert vanilla.releases["22w11a"].type == "snapshot"

    ctx.data.loot_table.merge(
        vanilla.mount("data/minecraft/loot_table").data.loot_table
    )
    ctx.data["demo"].recipe.merge(
        vanilla.mount("data/minecraft/recipe").data["minecraft"].recipe
    )

    client_jar = vanilla.mount("assets/minecraft/lang")
    minecraft = client_jar.assets["minecraft"]
    assert minecraft.languages.keys() == {"en_us"}
    vanilla.mount("assets/minecraft/lang/fr_fr.json")
    assert minecraft.languages.keys() == {"en_us"}
    vanilla.mount("assets/minecraft/lang/fr_fr.json", fetch_objects=True)
    assert minecraft.languages.keys() == {"en_us", "fr_fr"}
    vanilla.mount("assets/minecraft/lang/fr_fr.json")
    assert minecraft.languages.keys() == {"en_us", "fr_fr"}

    vanilla.mount("assets/minecraft/sounds/ui/toast/in.ogg")
    assert minecraft.sounds.keys() == set()
    vanilla.mount("assets/minecraft/sounds/ui/toast/in.ogg", fetch_objects=True)
    assert minecraft.sounds.keys() == {"ui/toast/in"}
    vanilla.mount("assets/minecraft/sounds/records", fetch_objects=True)
    assert len(minecraft.sounds) > 10

    ctx.require(
        load_vanilla(
            files=[
                "data/minecraft/tags/items/anvil.json",
                "assets/minecraft/blockstates/anvil.json",
            ],
            match="minecraft:entity/axolotl/*",
        )
    )
