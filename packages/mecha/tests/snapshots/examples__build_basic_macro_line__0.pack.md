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
function demo:thing {name: "steve", eval: "kill @a"}
```

`@function demo:thing`

```mcfunction
$say hello $(name)
$   say hello $(name)
$$(eval)
```
