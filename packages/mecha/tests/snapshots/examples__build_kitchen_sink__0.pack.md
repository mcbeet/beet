# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 9,
    "description": ""
  }
}
```

### demo

`@function demo:function_tag`

```mcfunction
say hello
execute as @a run function demo:with_tag
```

`@function demo:implicit_execute`

```mcfunction
execute as @a at @s align xyz run summon armor_stand ~ ~ ~ {Tags: ["position_history", "new"], Invisible: 1b, Marker: 1b}
execute if score @s obj matches 2 run say hi
```

`@function demo:messages`

```mcfunction
tellraw @p {"text": "hello", "color": "red"}
data modify storage imp:io words set value ["alpha", "beta", "gamma", "delta"]
```

`@function demo:nesting`

```mcfunction
execute as @a at @s run function demo:nesting/nested_execute_0
execute as @a at @s if score @s tmp matches 1 run function demo:nesting/nested_execute_1
execute as @a at @s run say 1
execute as @a at @s run say 2
execute as @a at @s if score @s tmp matches 1 run say 1
execute as @a at @s if score @s tmp matches 1 run say 2
execute if data storage imp:temp iter.words.remaining[] run function demo:nesting/loop
execute if score @s tmp matches 0 run function demo:nesting/nested_execute_2
execute if score @s tmp matches 0 at @e[type=pig] unless entity @e[type=sheep] run setblock ~ ~ ~ dirt
```

`@function demo:with_tag`

```mcfunction
say world
```

`@function demo:my_load`

```mcfunction
say loaded
```

`@function demo:also_with_tag`

```mcfunction
say foo
```

`@function demo:nesting/nested_execute_0`

```mcfunction
say hello
say world
```

`@function demo:nesting/nested_execute_1`

```mcfunction
say hello
say world
```

`@function demo:nesting/loop`

```mcfunction
say wow
execute if data storage imp:temp iter.words.remaining[] run function demo:nesting/loop
```

`@function demo:nesting/nested_execute_2`

```mcfunction
execute at @e[type=pig] run setblock ~ ~ ~ stone
execute at @e[type=sheep] run setblock ~ ~ ~ dirt
```

`@function demo:nesting/foo`

```mcfunction
say this is a test
```

`@function_tag demo:abc`

```json
{
  "values": [
    "demo:also_with_tag",
    "demo:with_tag"
  ]
}
```

`@function_tag demo:xyz`

```json
{
  "values": [
    "demo:with_tag"
  ]
}
```

### minecraft

`@function_tag minecraft:tick`

```json
{
  "values": [
    "demo:function_tag"
  ]
}
```

`@function_tag minecraft:load`

```json
{
  "values": [
    "demo:my_load"
  ]
}
```
