# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 10,
    "description": ""
  }
}
```

### demo

`@function demo:foo`

```mcfunction
scoreboard players set @a foo 1
say @a[scores={thing=..9}]
execute if score @s wat matches 7 run scoreboard players operation @s wat = @p[tag=target, scores={wow=1..}, sort=nearest] wow
```

### gather_objectives

`@function gather_objectives:generated_0`

```mcfunction
say foo, thing, wat, wow
```
