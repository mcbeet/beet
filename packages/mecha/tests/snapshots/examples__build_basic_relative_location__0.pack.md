# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 26,
    "description": ""
  }
}
```

### demo

`@function demo:bar`

```mcfunction
say hello
```

`@function demo:folder/wat`

```mcfunction
function demo:bar
```

`@function demo:foo`

```mcfunction
function demo:folder/wat
function demo:bar
schedule function demo:other 1s
schedule clear demo:other
```

`@function demo:other`

```mcfunction
say delayed
```
