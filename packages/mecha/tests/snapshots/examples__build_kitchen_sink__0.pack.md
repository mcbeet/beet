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
`@function demo:implicit_execute`

```mcfunction
execute as @a at @s align xyz run summon armor_stand ~ ~ ~ {Tags: ["position_history", "new"], Invisible: 1b, Marker: 1b}
execute if score @s obj matches 2 run say hi
```
