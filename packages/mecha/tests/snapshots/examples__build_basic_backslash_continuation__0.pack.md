# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "min_format": [
      101,
      1
    ],
    "max_format": [
      101,
      1
    ],
    "description": ""
  }
}
```

### demo

`@function demo:foo`

```mcfunction
execute as @a[tag=blob] run function demo:foo
say hello
```
