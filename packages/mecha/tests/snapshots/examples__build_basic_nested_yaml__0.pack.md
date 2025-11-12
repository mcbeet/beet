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

`@function demo:foo`

```mcfunction
tellraw @a ["", {text: "hello", color: "red"}]
tellraw @a ["", {text: "hello", color: "red"}]
summon armor_stand ~ ~ ~ {Tags: ["position_history", "new"], Invisible: 1b, Marker: 1b}
summon armor_stand ~ ~ ~ {Tags: ["position_history", "new"], Invisible: 1b, Marker: 1b}
tellraw @s {text: "Hover me!", hoverEvent: {action: "show_text", value: "Hi!"}}
tellraw @a {text: "Hello # there"}
tellraw @a {text: 'Hello" # "there'}
data merge storage demo:foo {custom_stuff: {list_of_lists: [[0, 0, 0], [1, 1, 1]], normal_lists: [[0, 0, 0], [1, 1, 1]]}, something_else: [{type: "foo", foo: 42}, {type: "bar", bar: 99}], byte_array: [B; 1b, 1b, 0b, 1b], item1: {id: "player_head", count: 1b, components: {"minecraft:profile": "herobrine"}}, item2: {id: "player_head", count: 1b, components: {"minecraft:profile": "herobrine"}}}
```
