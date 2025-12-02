# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "min_format": [
      88,
      0
    ],
    "max_format": [
      88,
      0
    ],
    "description": ""
  },
  "overlays": {
    "entries": [
      {
        "directory": "demo_stuff",
        "min_format": [
          88,
          0
        ],
        "max_format": [
          88,
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
