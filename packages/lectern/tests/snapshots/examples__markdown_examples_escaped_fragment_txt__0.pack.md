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
@function demo:foo
@@blah demo:foo
@function(@@) demo:bar
@@function(@@@) demo:bar
@function demo:bar
```
