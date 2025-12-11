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
# [source_map] src/data/demo/functions/foo.mcfunction
say abc
execute as @p run say something
execute as @p run function demo:foo/nested_execute_0
```

`@function demo:thing`

```mcfunction
# [source_map] basic_source_map:generated_0
say 456
```

`@function demo:foo/nested_execute_0`

```mcfunction
# [source_map] src/data/demo/functions/foo.mcfunction
say foo
say bar
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
