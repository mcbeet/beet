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

### tutorial

`@function tutorial:greeting`

```mcfunction
say Hello, world!
```

### minecraft

`@function_tag minecraft:load`

```json
{
  "values": ["tutorial:greeting"]
}
```
