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
execute as @a run function demo:bar/generated/0x0
```

`@function demo:foo`

```mcfunction
execute as @a run function demo:foo/generated/0x0
```

`@function demo:bar/generated/0x0`

```mcfunction
say test
say bar
```

`@function demo:foo/generated/0x0`

```mcfunction
say test
say foo
```

`@function demo:foo/stuff/generated/0x0`

```mcfunction
say test
say foo
```

`@function demo:foo/stuff`

```mcfunction
execute as @a run function demo:foo/stuff/generated/0x0
```
