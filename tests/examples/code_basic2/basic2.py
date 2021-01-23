from beet import Blockstate, Context, Model


def beet_default(ctx: Context):
    ctx.assets["minecraft:block/basic2/funky_model"] = Model(
        source_path=ctx.directory / "funky_model.json"
    )
    ctx.assets["minecraft:block/stone"] = Model(
        {
            "parent": "block/basic2/funky_model",
            "textures": {
                "foo": "minecraft:block/stone",
                "bar": "minecraft:block/dirt",
            },
        }
    )
    ctx.assets["minecraft:stone"] = Blockstate(
        {"variants": {"": [{"model": "minecraft:block/stone"}]}}
    )
