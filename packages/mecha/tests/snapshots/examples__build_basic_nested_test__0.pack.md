# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 48,
    "description": ""
  }
}
```

### demo

`@function demo:stuff`

```mcfunction
setblock ~ ~ ~ stone
execute if block ~ ~ ~ stone run function demo:stuff/remove
```

`@function demo:stuff/remove`

```mcfunction
setblock ~ ~ ~ air
```

`@function demo:foo`

```mcfunction
execute as @p run say this is a test
```

`@function demo:stuff/blah`

```mcfunction
execute if block ~ ~ ~ stone run say success
```

`@function demo:stuff/remove/generated_0`

```mcfunction
say 1
```

`@function demo:stuff/remove/generated_1`

```mcfunction
say 2
```
