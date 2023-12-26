# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 26,
    "description": ""
  }
}
```

### demo

`@function demo:foo`

```mcfunction
tellraw @p {"text": "empty"}
```

`@loot_table demo:foo`

```json
{
  "pools": []
}
```

`@loot_table demo:bar`

```json
{
  "pools": []
}
```
