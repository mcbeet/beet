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
        "formats": 12,
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
