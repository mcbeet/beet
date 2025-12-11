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
