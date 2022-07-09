# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 10,
    "description": ""
  }
}
```

### demo

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
```
