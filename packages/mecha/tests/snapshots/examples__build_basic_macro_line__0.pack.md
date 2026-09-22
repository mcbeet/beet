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
  }
}
```

### demo

`@function demo:foo`

```mcfunction
function demo:thing {name: "steve", eval: "kill @a"}
```

`@function demo:thing`

```mcfunction
$say hello $(name)
$   say hello $(name)
$$(eval)
```
