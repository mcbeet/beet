# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 41,
    "description": ""
  }
}
```

### demo

`@function demo:foo`

```mcfunction
execute if entity @e[type=pig] run return 1
return 0
```
