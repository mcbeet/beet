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

`@function(strip_final_newline) demo:stuff`

```mcfunction

```

`@loot_table demo:foo`

```json
{
  "pools": [
    {
      "rolls": 1,
      "entries": [
        {
          "type": "item",
          "name": "minecraft:diamond",
          "functions": [
            {
              "function": "minecraft:set_nbt",
              "tag": "{custom: {value: \"owo\"}}"
            }
          ]
        }
      ]
    }
  ]
}
```

`@loot_table demo:bar`

```json
{
  "pools": [
    {
      "rolls": 1,
      "entries": [
        {
          "type": "item",
          "name": "minecraft:emerald",
          "functions": [
            {
              "function": "minecraft:set_nbt",
              "tag": "{custom: {item: \"owo\", json_text_component: '{\"function\": \"minecraft:set_nbt\", \"tag\": \"{who_cares: \\\\\"owo\\\\\"}\", \"text\": \"nonsense\", \"color\": \"red\"}'}}"
            }
          ]
        }
      ]
    }
  ]
}
```
