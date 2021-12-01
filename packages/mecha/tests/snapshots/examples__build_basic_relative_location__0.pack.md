# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 7,
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
```
