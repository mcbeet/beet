# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 8,
    "description": ""
  }
}
```

### demo

`@function demo:foo`

```mcfunction
execute as @a at @s run function demo:thing4
execute as @a at @s run function demo:thing5
execute as @a at @s run function demo:foo/nested_execute_0
execute as @a at @s run function demo:foo/nested_execute_1
execute as @a at @s run say hello
execute as @a at @s run say world
execute as @a at @s anchored eyes facing 0 0 0 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.6] run function demo:foo/nested_execute_2
say foo bar
execute as @a run say hello
execute as @a at @s anchored eyes facing 0 0 0 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.6] run say I'm facing the target!
execute as @a at @s anchored eyes facing 0 0 0 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.6] run say oh wow
execute as @a at @s anchored eyes facing 0 0 0 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.6] run say this is duplicated
```

`@function demo:thing2`

```mcfunction
say this is a test
```

`@function demo:thing3`

```mcfunction
say this is a test
```

`@function demo:thing4`

```mcfunction
setblock ~ ~ ~ stone_pressure_plate
setblock ~ ~-1 ~ tnt
setblock ~ ~-2 ~ stone
```

`@function demo:thing5`

```mcfunction
setblock ~ ~ ~ stone_pressure_plate
setblock ~ ~-1 ~ tnt
setblock ~ ~-2 ~ stone
```

`@function demo:foo/nested_execute_0`

```mcfunction
setblock ~ ~ ~ stone_pressure_plate
setblock ~ ~-1 ~ tnt
setblock ~ ~-2 ~ stone
```

`@function demo:foo/nested_execute_1`

```mcfunction
setblock ~ ~ ~ stone_pressure_plate
setblock ~ ~-1 ~ tnt
setblock ~ ~-2 ~ stone
```

`@function demo:foo/nested_execute_2`

```mcfunction
say foo
say bar
```

`@function demo:thing1`

```mcfunction
say hello
say world
```
