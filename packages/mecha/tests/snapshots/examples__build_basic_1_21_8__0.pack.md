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
