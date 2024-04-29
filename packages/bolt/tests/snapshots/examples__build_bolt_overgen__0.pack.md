# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 41,
    "description": ""
  },
  "overlays": {
    "entries": [
      {
        "formats": {
          "min_inclusive": 18,
          "max_inclusive": 19
        },
        "directory": "demo_stuff"
      }
    ]
  }
}
```

### demo

`@function demo:foo`

```mcfunction
value = "abc"
print(value)
say this should be left untouched
```

## Overlay `demo_stuff`

`@overlay demo_stuff`

### demo

`@function demo:foo`

```mcfunction
say stuff
```

`@endoverlay`
