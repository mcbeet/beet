# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 14,
    "description": ""
  }
}
```

### demo

`@function demo:foo`

```mcfunction
execute if entity @e[type=pig] run return 123
return 77
say 99999
function demo:thing
return 0
```

`@function demo:thing`

```mcfunction
return 42
```

## Resource pack

`@resource_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 14,
    "description": ""
  }
}
```
