# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 10,
    "description": ""
  }
}
```

### demo

`@function demo:foo`

```mcfunction
# [source_map] src/data/demo/functions/foo.mcfunction
say abc
```

`@function demo:thing`

```mcfunction
# [source_map] basic_source_map:generated_0
say 456
```

`@function demo:bar`

```mcfunction
# [source_map] src/data/demo/functions/foo.mcfunction
say def
```

### basic_source_map

`@function basic_source_map:generated_0`

```mcfunction
# [source_map] basic_source_map:generated_0
say 123
```
