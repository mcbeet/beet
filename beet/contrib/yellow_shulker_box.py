"""Plugin that includes the yellow shulker box loot table."""


from beet import Context, LootTable


def beet_default(ctx: Context):
    alternatives = [
        {
            "type": "minecraft:dynamic",
            "name": "minecraft:contents",
            "conditions": [
                {
                    "condition": "minecraft:match_tool",
                    "predicate": {
                        "items": ["minecraft:air"],
                        "nbt": "{drop_contents:1b}",
                    },
                }
            ],
        },
        {
            "type": "minecraft:item",
            "name": "minecraft:yellow_shulker_box",
            "functions": [
                {
                    "function": "minecraft:copy_name",
                    "source": "block_entity",
                },
                {
                    "function": "minecraft:copy_nbt",
                    "source": "block_entity",
                    "ops": [
                        {
                            "source": "Lock",
                            "target": "BlockEntityTag.Lock",
                            "op": "replace",
                        },
                        {
                            "source": "LootTable",
                            "target": "BlockEntityTag.LootTable",
                            "op": "replace",
                        },
                        {
                            "source": "LootTableSeed",
                            "target": "BlockEntityTag.LootTableSeed",
                            "op": "replace",
                        },
                    ],
                },
                {
                    "function": "minecraft:set_contents",
                    "entries": [
                        {
                            "type": "minecraft:dynamic",
                            "name": "minecraft:contents",
                        }
                    ],
                },
            ],
        },
    ]

    ctx.data["minecraft:blocks/yellow_shulker_box"] = LootTable(
        {
            "type": "minecraft:block",
            "pools": [
                {
                    "rolls": 1,
                    "entries": [
                        {"type": "minecraft:alternatives", "children": alternatives}
                    ],
                }
            ],
        }
    )
