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
say hello
execute as @a run function demo:stuff
```

`@function demo:stuff`

```mcfunction
say a
say b
say c
```

## Overlay `dummy_overlay`

`@overlay dummy_overlay`

### demo

`@function demo:foo`

```mcfunction
say hello from overlay
execute as @a run function demo:stuff
```

`@function demo:stuff`

```mcfunction
say 1
say 2
say 3
```

`@endoverlay`
