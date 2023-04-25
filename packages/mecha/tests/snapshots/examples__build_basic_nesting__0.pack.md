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
schedule function demo:schedule1 42
execute if score global tmp matches 7 run schedule function demo:schedule2 42 append
schedule function demo:schedule3 42 replace
say foo1
say foo2
say foo3
say after
```

`@function demo:wat`

```mcfunction
function demo:wat/nested_execute_0
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

`@function demo:schedule1`

```mcfunction
say hello1
```

`@function demo:schedule2`

```mcfunction
say hello2
```

`@function demo:schedule3`

```mcfunction
say hello3
```

`@function demo:thing1`

```mcfunction
say hello
say world
```

`@function demo:queue`

```mcfunction
say queue1
say queue2
say queue3
```

`@function demo:stack`

```mcfunction
say stack3
say stack2
say stack1
```

`@function demo:abc`

```mcfunction
say hello
```

`@function demo:wat/nested_execute_0`

```mcfunction
say 1
say 2
```
