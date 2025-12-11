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

### demo

`@function demo:foo`

```mcfunction
summon zombie ~ ~ ~ {Tags: ["my_custom_mob", "custom_summon_init"]}
execute as @e[type=minecraft:zombie, tag=custom_summon_init] at @s run function demo:foo/nested_execute_0
summon zombie 1 2 3 {Tags: ["custom_summon_init"]}
execute as @e[type=minecraft:zombie, tag=custom_summon_init] at @s run function demo:foo/nested_execute_1
summon zombie 1 2 3 {Tags: ["using_nested_yaml"]}
summon zombie ~ ~ ~ {Tags: ["custom_summon_init"]}
execute as @e[type=minecraft:zombie, tag=custom_summon_init] at @s run function demo:foo/nested_execute_2
summon zombie ~1 ~2 ~3 {Tags: ["custom_summon_init"]}
execute as @e[type=minecraft:zombie, tag=custom_summon_init] at @s run function demo:foo/nested_execute_3
```

`@function demo:foo/nested_execute_0`

```mcfunction
say Hello I just spawned!
effect give @e[distance=..3] poison
tag @s remove custom_summon_init
```

`@function demo:foo/nested_execute_1`

```mcfunction
say no nbt
tag @s remove custom_summon_init
```

`@function demo:foo/nested_execute_2`

```mcfunction
say no position or nbt
tag @s remove custom_summon_init
```

`@function demo:foo/nested_execute_3`

```mcfunction
say hello
tag @s remove custom_summon_init
```
