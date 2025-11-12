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
  }
}
```

### demo

`@function demo:foo`

```mcfunction
dialog show @s {title: "aa", type: "notice"}
dialog show @s minecraft:test
waypoint modify @s color hex FF0
waypoint modify @s color hex eE00ff
waypoint modify @s color blue
```
