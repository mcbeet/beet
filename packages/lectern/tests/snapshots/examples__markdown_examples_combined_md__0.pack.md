# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "description": "hello",
    "pack_format": 7
  }
}
```

### demo

`@function demo:foo`

```mcfunction
say foo
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

### minecraft

`@blockstate minecraft:grass_block`

```json
{
  "variants": {
    "snowy=false": { "model": "block/grass_block" },
    "snowy=true": { "model": "block/grass_block_snow" }
  }
}
```
