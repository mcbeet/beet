# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 8,
    "description": ""
  }
}
```

### demo

`@function demo:foo`

```mcfunction
say Hello @a[tag=!registered]
execute if score #init temp = #wat temp run say Hello @a[tag=hi]
```
