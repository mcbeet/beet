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

`@function demo:0`

```mcfunction
data merge storage smithed:log {message: '["Could not find ",{"text":"#smithed.prevent_aggression 0.0.1","color":"red"}]', type: "ERROR"}
function #smithed:core/pub/technical/tools/log
```

`@function demo:foo`

```mcfunction
say 123
```

`@function demo:generated`

```mcfunction
execute if score #smithed.core load.status matches 1 run function demo:0
```
