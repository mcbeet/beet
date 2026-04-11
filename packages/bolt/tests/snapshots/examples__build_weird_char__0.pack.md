# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "min_format": [
      101,
      1
    ],
    "max_format": [
      101,
      1
    ],
    "description": ""
  }
}
```

### example

`@function example:say`

```mcfunction
say "🗡 "
tellraw @a {text: "\U0001f5e1"}
function example:load
```

`@function example:load`

```mcfunction
team add duels.team_1 "Duels Team 1"
team add duels.team_2 "Duels Team 2"
team modify duels.team_1 friendlyFire false
team modify duels.team_1 prefix "\U0001f5e1 "
team modify duels.team_1 seeFriendlyInvisibles false
team modify duels.team_2 friendlyFire false
team modify duels.team_2 prefix "\U0001f5e1 "
team modify duels.team_2 seeFriendlyInvisibles false
```

`@recipe example:sharp_diamond`

```json
{
  "type": "minecraft:crafting_shapeless",
  "ingredients": [
    [
      "minecraft:diamond"
    ]
  ],
  "result": {
    "id": "minecraft:diamond",
    "components": {
      "minecraft:item_name": "\ud83d\udde1"
    }
  }
}
```
