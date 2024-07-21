# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 48,
    "description": ""
  }
}
```

### demo

`@function demo:foo`

```mcfunction
tellraw @p {"text": "empty"}
```

`@loot_table demo:foo`

```json
{
  "pools": []
}
```

`@loot_table demo:zombified_piglin`

```json
{
  "type": "minecraft:fishing",
  "pools": [
    {
      "rolls": 1,
      "entries": [
        {
          "type": "minecraft:loot_table",
          "name": "gm4_orb_of_ankou:items/soul_essence/aggressive"
        }
      ],
      "conditions": [
        {
          "condition": "minecraft:table_bonus",
          "enchantment": "minecraft:looting",
          "chances": [
            6e-05,
            0.00024,
            0.0015,
            0.00492,
            0.01158,
            0.02256,
            0.03894,
            0.0618,
            0.09222,
            0.13128,
            0.18006
          ]
        }
      ]
    },
    {
      "rolls": 1,
      "entries": [
        {
          "type": "minecraft:loot_table",
          "name": "gm4_orb_of_ankou:items/soul_essence/incombustible"
        }
      ],
      "conditions": [
        {
          "condition": "minecraft:table_bonus",
          "enchantment": "minecraft:looting",
          "chances": [
            4.8e-05,
            0.000192,
            0.0012,
            0.003936,
            0.009264,
            0.018048,
            0.031152,
            0.04944,
            0.073776,
            0.105024,
            0.144048
          ]
        }
      ]
    },
    {
      "rolls": 1,
      "entries": [
        {
          "type": "minecraft:loot_table",
          "name": "gm4_orb_of_ankou:items/soul_essence/lifeless"
        }
      ],
      "conditions": [
        {
          "condition": "minecraft:table_bonus",
          "enchantment": "minecraft:looting",
          "chances": [
            5.5e-05,
            0.00022,
            0.001375,
            0.00451,
            0.010615,
            0.02068,
            0.035695,
            0.05665,
            0.084535,
            0.12034,
            0.165055
          ]
        }
      ]
    },
    {
      "rolls": 1,
      "entries": [
        {
          "type": "minecraft:loot_table",
          "name": "gm4_orb_of_ankou:items/soul_essence/rushing"
        }
      ],
      "conditions": [
        {
          "condition": "minecraft:table_bonus",
          "enchantment": "minecraft:looting",
          "chances": [
            3.7e-05,
            0.000148,
            0.000925,
            0.003034,
            0.007141,
            0.013912,
            0.024013,
            0.03811,
            0.056869,
            0.080956,
            0.111037
          ]
        }
      ]
    }
  ]
}
```

`@loot_table demo:bar`

```json
{
  "pools": []
}
```
