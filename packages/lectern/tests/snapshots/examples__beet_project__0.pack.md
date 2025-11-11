# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "min_format": [
      88,
      0
    ],
    "max_format": [
      88,
      0
    ],
    "description": ""
  }
}
```

### demo

`@function demo:define_1`

```mcfunction
say azertyuiop
```

`@function demo:define_2`

```mcfunction
say azertyuiopqsdfghjklm
```

`@function demo:define_3`

```mcfunction
say 2 + 2 is 4 (end of citation)
```

`@function demo:foo`

```mcfunction
say foo
```

`@function demo:bar`

```mcfunction
say bar
```

`@function demo:script_foo`

```mcfunction
say something

```

`@function demo:script_0`

```mcfunction
say 0
```

`@function demo:script_1`

```mcfunction
say 1
```

`@function demo:script_2`

```mcfunction
say 2
```

`@function demo:script_3`

```mcfunction
say 3
```

`@function demo:script_4`

```mcfunction
say 4
```

`@function demo:script_5`

```mcfunction
say 5
```

`@function demo:script_6`

```mcfunction
say 6
```

`@function demo:script_7`

```mcfunction
say 7
```

`@function demo:script_8`

```mcfunction
say 8
```

`@function demo:script_9`

```mcfunction
say 9

```

`@function demo:script_nested`

```mcfunction
say wow
```

`@function demo:script_please_avoid_this`

```mcfunction
say no
```

`@function demo:a`

```mcfunction
say tagged a
```

`@function demo:b`

```mcfunction
say tagged b
```

`@function_tag demo:foo`

```json
{
  "values": [
    "with_beet:foo"
  ]
}
```

`@function_tag demo:abc`

```json
{
  "values": [
    "with_beet:bar"
  ]
}
```

`@function_tag demo:123`

```json
{
  "values": [
    "with_beet:bar"
  ]
}
```

### custom

`@function custom:hello`

```mcfunction
say hello
say bye
say hello
say bye
say hello
say bye
say hello
say bye
say hello
say bye
say hello
say bye
say hello
say bye
say hello
say bye
say hello
say bye
say hello
say bye
say hello
say bye
say hello
say bye
say hello
say bye
say hello
say bye
say hello
say bye
say hello
say bye
say hello
say bye
say hello
say bye
say hello
say bye
say hello
say bye
say hello
say bye
say hello
say bye
say hello
say bye
say hello
say bye
```

### hello

`@function hello:greetings`

```mcfunction
say Hello, Alice!
say Hello, Bob!
```

### embedded

`@function embedded:foo`

```mcfunction
say foo
```

`@function embedded:bar`

```mcfunction
say bar
```

### with_beet

`@function with_beet:abc`

```mcfunction
function with_beet:def
```

`@function with_beet:def`

```mcfunction
say relative
```

`@function with_beet:a_relative`

```mcfunction
say tagged a_relative
```

`@function with_beet:load`

```mcfunction
say before
say tagged load
```

`@function with_beet:wow`

```mcfunction
say tagged wow
```

`@function with_beet:foo`

```mcfunction
say tagged foo
```

`@function with_beet:bar`

```mcfunction
say tagged bar
```

### from_script

`@function from_script:hello`

```mcfunction
say hello
```

`@function from_script:thing`

```mcfunction
say 0
say 1
say 2
say 3
say 4
say 5
say 6
say 7
say 8
say 9
```

### minecraft

`@loot_table minecraft:blocks/yellow_shulker_box`

```json
{
  "type": "minecraft:block",
  "pools": [
    {
      "rolls": 1,
      "entries": [
        {
          "type": "minecraft:alternatives",
          "children": [
            {
              "type": "minecraft:dynamic",
              "name": "minecraft:contents",
              "conditions": [
                {
                  "condition": "minecraft:match_tool",
                  "predicate": {
                    "items": [
                      "minecraft:air"
                    ],
                    "nbt": "{drop_contents:1b}"
                  }
                }
              ]
            },
            {
              "type": "minecraft:item",
              "name": "minecraft:yellow_shulker_box",
              "functions": [
                {
                  "function": "minecraft:copy_name",
                  "source": "block_entity"
                },
                {
                  "function": "minecraft:copy_nbt",
                  "source": "block_entity",
                  "ops": [
                    {
                      "source": "Lock",
                      "target": "BlockEntityTag.Lock",
                      "op": "replace"
                    },
                    {
                      "source": "LootTable",
                      "target": "BlockEntityTag.LootTable",
                      "op": "replace"
                    },
                    {
                      "source": "LootTableSeed",
                      "target": "BlockEntityTag.LootTableSeed",
                      "op": "replace"
                    }
                  ]
                },
                {
                  "function": "minecraft:set_contents",
                  "entries": [
                    {
                      "type": "minecraft:dynamic",
                      "name": "minecraft:contents"
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

`@function_tag minecraft:tick`

```json
{
  "values": [
    "isolated:thing",
    "with_beet:wow"
  ]
}
```

`@function_tag minecraft:load`

```json
{
  "values": [
    "demo:a",
    "demo:b",
    "with_beet:a_relative",
    "with_beet:load"
  ]
}
```

### isolated

`@function isolated:thing`

```mcfunction
say this is not affected
```

`@function isolated:plugin_test/foo`

```mcfunction
say running isolated:plugin_test/foo
say hello
```

`@function isolated:plugin_test/foo_copy`

```mcfunction
say running isolated:plugin_test/foo
say hello
```

`@function isolated:message_demo`

```mcfunction
tellraw @a ["", {"text": "hello", "color": "red"}]
```

## Resource pack

`@resource_pack pack.mcmeta`

```json
{
  "pack": {
    "min_format": [
      69,
      0
    ],
    "max_format": [
      69,
      0
    ],
    "description": ""
  }
}
```

`@resource_pack pack.png`

![resource_pack.png](data:image/png;base64,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)

### minecraft

`@resource_pack assets/minecraft/sounds.json`

```json
{
  "block.note_block.bit_1": {
    "sounds": [
      "block/note_block/bit_1"
    ],
    "subtitle": "subtitles.block.note_block.note"
  }
}
```
