# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 18,
    "description": ""
  }
}
```

### demo

`@function demo:foo`

```mcfunction
function demo:foo/thing1
function demo:foo/__
function demo:foo/foo_bar_
```

`@function demo:foo/thing1/thing2`

```mcfunction
function demo:foo/thing1/thing2/thing003/hello
say demo:foo/thing1/thing2/thing75bcd15/hello
```

`@function demo:foo/thing1/blob`

```mcfunction
say ('demo:foo/thing1/blob', 'demo:foo/thing1/dem')
```

`@function demo:foo/thing1`

```mcfunction
execute as @a run function demo:foo/thing1/thing2
schedule function demo:foo/thing1/blob 2s append
```

`@function demo:welp`

```mcfunction
execute if predicate demo:welp run say yes
```
