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
say hello
```

### minecraft

`@function_tag minecraft:load`

```json
{
  "values": [
    "demo:foo"
  ]
}
```
