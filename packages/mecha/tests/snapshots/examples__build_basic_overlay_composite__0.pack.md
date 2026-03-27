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
        "min_format": [
          94,
          1
        ],
        "max_format": [
          94,
          1
        ],
        "directory": "old"
      }
    ]
  }
}
```

### demo

`@function demo:foo`

```mcfunction
scoreboard objectives add roll_dice dummy
execute store result score @s roll_dice run random value 1..6
```

## Overlay `old`

`@overlay old`

### demo

`@function demo:foo`

```mcfunction
scoreboard objectives add roll_dice dummy
scoreboard objectives setdisplay belowName roll_dice
```

`@endoverlay`
