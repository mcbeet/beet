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

`@function demo:foo`

```mcfunction
execute as @p run say this is a test
```

`@function demo:stuff`

```mcfunction
setblock ~ ~ ~ stone
execute if block ~ ~ ~ stone run function demo:stuff/remove
```

`@function demo:stuff/blah`

```mcfunction
execute if block ~ ~ ~ stone run say success
```

`@function demo:stuff/remove`

```mcfunction
setblock ~ ~ ~ air
```

`@function demo:stuff/remove/generated_0`

```mcfunction
say 1
```

`@function demo:stuff/remove/generated_1`

```mcfunction
say 2
```
