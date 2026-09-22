# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "min_format": [
      121,
      0
    ],
    "max_format": [
      121,
      0
    ],
    "description": ""
  },
  "overlays": {
    "entries": [
      {
        "directory": "dummy",
        "min_format": [
          121,
          0
        ],
        "max_format": [
          121,
          0
        ]
      }
    ]
  }
}
```

### demo

`@function demo:foo`

```mcfunction
say 123
```

## Overlay `dummy`

`@overlay dummy`

### demo

`@function demo:foo`

```mcfunction
say 456
```

`@endoverlay`
