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
        "directory": "dummy_overlay",
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
say my 123
```

## Overlay `dummy_overlay`

`@overlay dummy_overlay`

### demo

`@function demo:foo`

```mcfunction
say 3
say 123
```

`@endoverlay`
