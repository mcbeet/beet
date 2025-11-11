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
@function demo:foo
@@blah demo:foo
@function(@@) demo:bar
@@function(@@@) demo:bar
@function demo:bar
```
