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
say hello
```

`@function demo:bar`

```mcfunction
say world
```

### minecraft

`@function_tag minecraft:tick`

```json
{
  "values": [
    "demo:foo",
    "demo:bar"
  ]
}
```
