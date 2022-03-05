# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 9,
    "description": ""
  }
}
```

### demo

`@function demo:foo`

```mcfunction
tellraw @a ["", {"text": "hello", "color": "red"}]
tellraw @a ["", {"text": "hello", "color": "red"}]
summon armor_stand ~ ~ ~ {Tags: ["position_history", "new"], Invisible: 1b, Marker: 1b}
summon armor_stand ~ ~ ~ {Tags: ["position_history", "new"], Invisible: 1b, Marker: 1b}
tellraw @s {"text": "Hover me!", "hoverEvent": {"action": "show_text", "value": "Hi!"}}
tellraw @a {"text": "Hello # there"}
tellraw @a {"text": "Hello\" # \"there"}
data merge storage demo:foo {custom_stuff: {list_of_lists: [[0, 0, 0], [1, 1, 1]], normal_lists: [[0, 0, 0], [1, 1, 1]]}, something_else: [{type: "foo", foo: 42}, {type: "bar", bar: 99}], byte_array: [B; 1B, 1B, 0B, 1B]}
```
