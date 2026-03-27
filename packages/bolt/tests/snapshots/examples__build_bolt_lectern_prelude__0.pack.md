# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "min_format": [
      94,
      1
    ],
    "max_format": [
      94,
      1
    ],
    "description": ""
  },
  "overlays": {
    "entries": [
      {
        "directory": "dummy",
        "min_format": [
          94,
          1
        ],
        "max_format": [
          94,
          1
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
