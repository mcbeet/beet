# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 14,
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

## Resource pack

`@resource_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 14,
    "description": ""
  }
}
```
