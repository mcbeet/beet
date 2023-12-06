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
value = 123
print(value)
say this should be left untouched
```

`@function demo:stuff/abc`

```mcfunction
say 123
```
