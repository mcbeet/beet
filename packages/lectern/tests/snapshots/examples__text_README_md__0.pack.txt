@data_pack pack.mcmeta
{
  "pack": {
    "pack_format": 6,
    "description": ""
  }
}

@function tutorial:greeting
say Hello, world!

@function tutorial:obtained_dead_bush
say You obtained a dead bush!

@advancement tutorial:obtained_dead_bush
{
  "criteria": {
    "dead_bush": {
      "trigger": "minecraft:inventory_changed",
      "conditions": {
        "items": [
          {
            "item": "minecraft:dead_bush"
          }
        ]
      }
    }
  },
  "requirements": [
    [
      "dead_bush"
    ]
  ],
  "rewards": {
    "function": "tutorial:obtained_dead_bush"
  }
}

@function_tag minecraft:load
{
  "values": ["tutorial:greeting"]
}

@loot_table minecraft:blocks/diamond_ore
{
  "pools": [
    {
      "rolls": 1,
      "entries": [
        {
          "type": "minecraft:item",
          "name": "minecraft:dead_bush"
        }
      ]
    }
  ]
}
