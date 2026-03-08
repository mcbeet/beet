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
function #name:
function #name:name/
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

`@function namespace:error/nested/nested`

```mcfunction
say from nested 2
```

`@function namespace:error/nested`

```mcfunction
say from nested 1
function namespace:error/nested/nested
```

`@function namespace:nested/nested`

```mcfunction
say from nested 2
```

`@function namespace:nested`

```mcfunction
say from nested 1
function namespace:nested/nested
```

`@function namespace:defining/nested/nested`

```mcfunction
say from nested 2
```

`@function namespace:defining/nested`

```mcfunction
say from nested 1
function namespace:defining/nested/nested
```

`@function namespace:error`

```mcfunction
say error
function namespace:error/nested
```

`@function namespace:`

```mcfunction
say hello from empty function
function namespace:nested
```

`@function namespace:defining/`

```mcfunction
say weird syntax but it work
function namespace:defining/nested
```

### dm

`@function dm:nested/nested`

```mcfunction
say from nested 2
```

`@function dm:nested`

```mcfunction
say from nested 1
function dm:nested/nested
```

`@function dm:`

```mcfunction
say definig this function referenced
function dm:nested
```
