# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 12,
    "description": ""
  }
}
```

### demo

`@function demo:foo`

```mcfunction
execute if score @p tmp matches 1 run say hello
execute as @a at @s run setblock ~ ~ ~ stone
execute if score @p tmp matches 1 run say hello
execute as @a at @s run setblock ~ ~ ~ stone
execute if score @p tmp matches 1 run say hello
execute as @a at @s run setblock ~ ~ ~ stone
execute if score @p tmp matches 1 run say hello
execute as @a at @s run setblock ~ ~ ~ stone
execute store result score PLAYER_COUNT global if entity @a
execute store result score PLAYER_COUNT global if entity @a
summon pig
summon pig ~ ~ ~ {Fire: 120s}
execute summon pig run data merge entity @s {Fire: 120s}
execute summon pig run data merge entity @s {Fire: 120s}
execute at @a run summon pig
execute at @a run summon pig ~ ~ ~ {Fire: 120s}
execute at @a summon pig run data merge entity @s {Fire: 120s}
execute at @a summon pig run data merge entity @s {Fire: 120s}
```
