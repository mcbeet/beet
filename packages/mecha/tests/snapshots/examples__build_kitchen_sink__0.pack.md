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
`@function demo:messages`

```mcfunction
tellraw @p {"text": "hello", "color": "red"}
data modify storage imp:io words set value ["alpha", "beta", "gamma", "delta"]
```
`@function demo:nesting`

```mcfunction
execute as @a at @s run function demo:nesting/nested_execute_0
execute as @a at @s if score @s tmp matches 1 run function demo:nesting/nested_execute_1
function demo:nesting/foo
execute if data storage imp:temp iter.words.remaining[] run function demo:nesting/loop
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
`@function demo:nesting/foo`

```mcfunction
say this is a test
```
`@function demo:nesting/loop`

```mcfunction
say wow
execute if data storage imp:temp iter.words.remaining[] run function demo:nesting/loop
```
