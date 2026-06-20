# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "min_format": [
      107,
      1
    ],
    "max_format": [
      107,
      1
    ],
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
