# Lectern snapshot

## Data pack
`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 7,
    "description": ""
  }
}
```

### demo
`@function demo:foo`

```mcfunction
execute as @a at @s anchored eyes facing 0 0 0 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.6] run say I'm facing the target!
```
