# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 18,
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
