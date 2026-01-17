# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "min_format": [
      94,
      1
    ],
    "max_format": [
      94,
      1
    ],
    "description": ""
  }
}
```

### test

`@function test:test`

```mcfunction
item modify entity @s armor.feet [{function: "minecraft:set_components", components: {"minecraft:equippable": {slot: "feet", asset_id: "minecraft:netherite"}}}]
execute if predicate [{condition: "minecraft:all_of", terms: [{condition: "minecraft:random_chance", chance: 5}, {condition: "minecraft:value_check", value: 0, range: 0}]}, {condition: "minecraft:reference", name: "test:l"}] run say aaa
execute if predicate [{condition: "minecraft:value_check", name: "test:l", value: 0, range: {min: 0, max: 2}}, [{condition: "minecraft:value_check", name: "test:l", value: 0, range: {min: 1, max: 2}}]] run say bb
```
