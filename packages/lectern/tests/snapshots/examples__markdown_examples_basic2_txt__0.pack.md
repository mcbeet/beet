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
say foo
@functionn demo:foo
say still in the same function
@@@@
@ @ @
```

`@function demo:bar`

```mcfunction
say bar
 @function demo:bar
 say hello
  @function demo:bar
  say world
```
