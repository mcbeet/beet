# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "min_format": [
      94,
      1
    ],
    "max_format": [
      94,
      1
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
