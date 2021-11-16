# Lectern snapshot

## Data pack
`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 7,
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
```
