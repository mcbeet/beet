# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 12,
    "description": ""
  }
}
```

### demo

`@function demo:bar`

```mcfunction
execute as @a run function demo:zprivate/nested_execute_0
```

`@function demo:foo`

```mcfunction
execute as @a run function demo:special_execute_0
```

`@function demo:zprivate/nested_execute_0`

```mcfunction
say test
say bar
```

`@function demo:special_execute_0`

```mcfunction
say test
say foo
```
