# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 48,
    "description": ""
  }
}
```

### demo

`@function demo:bar`

```mcfunction
say macro foo
say macro foo 4
say macro foo 3
say macro foo 2
say macro foo 1
say macro foo
say macro foo 6
say macro foo 5
say macro foo 4
say macro foo 3
say macro foo 2
say macro foo 1
say macro foo
say macro foo 3
say macro foo 2
say macro foo 1
say macro foo
say hello @a[scores={x=42}]
setblock ~ ~ ~ air
setblock ~ ~ ~ stone
setblock 1 2 3 air
setblock 1 2 3 stone
say this is repeated twice
say this is repeated twice
tellraw @p {"text": "Custom symbols work"}
execute as @a run tellraw @p {"text": "Even inside execute"}
execute as @a run tellraw @p {"text": "Overload execute to allow implicit \"run\""}
tellraw @s {"text": "from demo:dummy_message"}
kill @e
say 42
```

`@function demo:foo`

```mcfunction
say macro foo
say macro foo 4
say macro foo 3
say macro foo 2
say macro foo 1
say macro foo
say macro foo 6
say macro foo 5
say macro foo 4
say macro foo 3
say macro foo 2
say macro foo 1
say macro foo
say macro foo 3
say macro foo 2
say macro foo 1
say macro foo
say hello @a[scores={x=42}]
setblock ~ ~ ~ air
setblock ~ ~ ~ stone
setblock 1 2 3 air
setblock 1 2 3 stone
say this is repeated twice
say this is repeated twice
tellraw @p {"text": "Custom symbols work"}
execute as @a run tellraw @p {"text": "Even inside execute"}
execute as @a run tellraw @p {"text": "Overload execute to allow implicit \"run\""}
tellraw @s {"text": "from demo:dummy_message"}
kill @e
say 42
```

`@function demo:redirect`

```mcfunction
function demo:redirect/nested_execute_2
function demo:redirect/nested_execute_3
execute if score foo bar matches 1 run say over!
execute as @e[type=pig] at @s if block ~ ~ ~ water run say blbllblb
execute as @e[type=bat] at @s run setblock ~ ~ ~ lava
execute if score foo bar matches 1 run execute as @e[type=chicken] at @s run kill @e[type=fox, distance=..4]
execute if score foo bar matches 1 as @e[type=chicken] at @s run kill @e[type=fox, distance=..4]
```

`@function demo:redirect/nested_execute_0`

```mcfunction
say ok
say ok
say ok
```

`@function demo:redirect/nested_execute_1`

```mcfunction
say ok
say ok
say ok
```

`@function demo:redirect/nested_execute_2`

```mcfunction
execute as @a run function demo:redirect/nested_execute_0
execute as @a run function demo:redirect/nested_execute_1
```

`@function demo:redirect/nested_execute_3`

```mcfunction
say world
say world
say world
```
