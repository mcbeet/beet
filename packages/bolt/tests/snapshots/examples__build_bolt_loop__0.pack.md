# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 26,
    "description": ""
  }
}
```

### demo

`@function demo:foo`

```mcfunction
tellraw @a {"text": "0"}
tellraw @a {"text": "1"}
tellraw @a {"text": "2"}
tellraw @a {"text": "3"}
scoreboard players set b global 0
function demo:foo/loop0
```

`@function demo:init`

```mcfunction
scoreboard objectives add global dummy
```

`@function demo:foo/loop0/nested_execute_0`

```mcfunction
tellraw @a {"score": {"name": "b", "objective": "global"}}
scoreboard players add b global 1
function demo:foo/loop0
```

`@function demo:foo/loop0`

```mcfunction
scoreboard players set tmp0 global 0
execute if score b global matches 4 run scoreboard players set tmp0 global 1
scoreboard players set tmp1 global 1
execute unless score tmp0 global matches 0 run scoreboard players set tmp1 global 0
execute unless score tmp1 global matches 0 run function demo:foo/loop0/nested_execute_0
```

### minecraft

`@function_tag minecraft:load`

```json
{
  "values": [
    "demo:init"
  ]
}
```
