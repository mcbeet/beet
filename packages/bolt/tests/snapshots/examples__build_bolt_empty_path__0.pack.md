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

`@function demo:`

```mcfunction
function demo:bar
function dm:
say YOLO
```

`@function demo:bar`

```mcfunction
say fooo
```

`@function demo:foo`

```mcfunction
say barr
```

### namespace

`@function namespace:error`

```mcfunction
say error
```
