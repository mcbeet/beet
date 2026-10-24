# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "min_format": [
      121,
      0
    ],
    "max_format": [
      121,
      0
    ],
    "description": ""
  }
}
```

### demo

`@function demo:foo`

```mcfunction
say foo
```

`@function demo:bar`

```mcfunction
say bar
```

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

### embedded

`@function embedded:foo`

```mcfunction
say foo
```

`@function embedded:bar`

```mcfunction
say bar
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
      97,
      1
    ],
    "max_format": [
      97,
      1
    ],
    "description": ""
  }
}
```

`@resource_pack pack.png`

![resource_pack.png](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAADIUlEQVR4nOWaSUsrURSEK2Wc5wEHFHWhOCEqLhxA9L+7cOM8bpyJ8xhnjZpHHWhJ6ORBIvrgnQ+Cac+9fe+tU9XtwsjOzk4SjiGcQziHcA7hHMI5hHMI5xDOIZxDOIdwDuEcwjmEcwjnEM4hnEM4h3AO4RzCOYRzCOcQziGcQziH35kcj8dxdHSE9/f3UO3h4cFqHx8f+C7JZBJnZ2f2ycTl5WXW2o8JEI/HMT8/j8fHR0Sj0bRaIpHA8vIytra2MoqTK7u7u1hfX0dBQUGodnNzg5WVFezt7f2eAIlEAqurq6itrUV3d3eovrGxkXGzAc/Pz3h7e/u6lojZnHJ9fY39/X10dXWhoaEhrfb6+oq1tTWUlZUhX5jPJB2QJHp6ekK1g4MD3N3dZawFxGIxLCwsmAj39/fmpIuLi9A41dX5xsZGtLS0hGKhWlVVVaiWC9FcJyhrylwkEsHc3BwKCwsxMDBg3bm9vcX29jaGh4dRVFSU9R7qpg4XiNDZ2Ynm5ubQON1L9fPzc1u3srISQ0NDKCkpMcs/PT1hfHzcnjW/5oBYLIbS0lJMTk5ienraNiVHKBbqSHt7O+rr6/96D4mncTqAnJSpg4rEyckJmpqaMDMzg4mJCby8vJgoyr0E6O/vtwZ8h2iuE7QJWVIiCG1eOVWHVFME9AmYnZ3F2NiYCRUg2y8uLpoTlH85YXR0NM01yrds3traas+T8vJy1NXV2fjT01OrLS0tpe1Na01NTf2sABUVFWb1z89P66TiUFxcbButrq7+Gqfu6gE1MjJic1I5PDw023d0dNhB9LbQoeSKAAmst4vE1cHlMK2r73rwtrW1fY09Pj7G1dWVRS9XorlOUNekvNQWOsDg4KCJkdplXQsdPvgeIOsGv9PPvr6+0Bhd9/b2YnNz06Kg16myr/UlTOpaaoCilM/bIJLP/wgpn4ELampqMuZQY/S3guraXL4oClpLa2S7V/BaTXXgjwrwP0E4h3AO4RzCOYRzCOcQziGcQziHcA7hHMI5hHMI5xDOIZxDOIdwDuEcwjmEcwjnEM4hnEM4h/96A/+aP+6DbQZYclT4AAAAAElFTkSuQmCC)

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
