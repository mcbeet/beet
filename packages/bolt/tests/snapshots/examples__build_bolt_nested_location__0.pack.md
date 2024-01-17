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

### ref

`@function ref:foo`

```mcfunction
function ref:foo
function ref:foo/thing
function ref:thing
execute if function ref:foo/condition run function ref:foo/action
```

`@function ref:bar/thing`

```mcfunction
function #ref:bar/thing/aaa
```

`@function ref:wat/thing`

```mcfunction
function #ref:wat/thing/bbb
```

`@function ref:foo/this/thing`

```mcfunction
function #ref:foo/this/thing/ccc
```

`@function ref:upthis/thing`

```mcfunction
function #ref:upthis/thing/ddd
```

`@function ref:bar`

```mcfunction
function ref:bar
function ref:bar/thing
function ref:thing
```

`@function ref:wat`

```mcfunction
function ref:wat
function ref:wat/thing
function ref:thing
```

`@function ref:foo/this`

```mcfunction
function ref:foo/this
function ref:foo/this/thing
function ref:foo/thing
```

`@function ref:upthis`

```mcfunction
function ref:upthis
function ref:upthis/thing
function ref:thing
```
