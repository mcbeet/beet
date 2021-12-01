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
function demo:thing1
execute as @a at @s run function demo:thing4
execute as @a at @s run function demo:thing5
execute as @a at @s run function demo:foo/nested_execute_0
execute as @a at @s run function demo:foo/nested_execute_1
execute as @a at @s run say hello
execute as @a at @s run say world
```

`@function demo:thing2`

```mcfunction
say this is a test
```

`@function demo:thing3`

```mcfunction
say this is a test
```

`@function demo:thing1`

```mcfunction
say hello
say world
function demo:thing2
function demo:thing3
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
