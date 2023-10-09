# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 18,
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
say calling function with parameters
function demo:bar0 {i: 10}
function demo:bar1 with entity @s
function demo:bar2 with entity @s Inventory
function demo:bar3 with storage demo:temp
function demo:bar4 with storage demo:temp args
function demo:bar5 with block ~ ~ ~
function demo:bar6 with block ~ ~ ~ Items
function demo:bar7 with storage demo:temp
function demo:bar8 with storage demo:temp args
say it's forbidden to define and call function with parameters
say error: Can't define function with arguments. Use 'execute function ...' instead.
say define and execute function with parameters
function demo:bar0 {i: 10}
function demo:bar1 with entity @s
function demo:bar2 with entity @s Inventory
function demo:bar3 with storage demo:temp
function demo:bar4 with storage demo:temp args
function demo:bar5 with block ~ ~ ~
function demo:bar6 with block ~ ~ ~ Items
function demo:bar7 with storage demo:temp
function demo:bar8 with storage demo:temp args
```

`@function demo:wat`

```mcfunction
function demo:wat/nested_execute_0
```

`@function demo:xct`

```mcfunction
function demo:xct/inner
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

`@function demo:bar0`

```mcfunction
say nested definition 0
```

`@function demo:bar1`

```mcfunction
say nested definition 1
```

`@function demo:bar2`

```mcfunction
say nested definition 2
```

`@function demo:bar3`

```mcfunction
say nested definition 3
```

`@function demo:bar4`

```mcfunction
say nested definition 4
```

`@function demo:bar5`

```mcfunction
say nested definition 5
```

`@function demo:bar6`

```mcfunction
say nested definition 6
```

`@function demo:bar7`

```mcfunction
say nested definition 7
```

`@function demo:bar8`

```mcfunction
say nested definition 8
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

`@function demo:xct/inner/nested_execute_0`

```mcfunction
say foo
say bar
```

`@function demo:xct/inner/nested_execute_1`

```mcfunction
say hello
say world
execute at @s run function demo:xct/inner/nested_execute_0
```

`@function demo:xct/inner`

```mcfunction
execute as @p run function demo:xct/inner/nested_execute_1
```
