# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 41,
    "description": ""
  }
}
```

### demo

`@function demo:foo`

```mcfunction
say hello
execute as @a run function demo:stuff
```

`@function demo:stuff`

```mcfunction
say a
say b
say c
```

## Overlay `dummy_overlay`

`@overlay dummy_overlay`

### demo

`@function demo:foo`

```mcfunction
say hello from overlay
execute as @a run function demo:stuff
```

`@function demo:stuff`

```mcfunction
say 1
say 2
say 3
```

`@endoverlay`
