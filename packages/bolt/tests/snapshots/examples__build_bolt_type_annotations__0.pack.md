# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 41,
    "description": ""
  }
}
```

### demo

`@function demo:foo`

```mcfunction
say hey
say 123
say {'b': <class 'int'>, 'c': list[int] | None, 'a': <class 'str'>, 'd': <class 'float'>, 'kwargs': <class 'object'>, 'return': tuple[int, ...]}
say False
say hello
say {'foo': <class 'int'>, 'bar': <class 'str'>}
say {'foo': list[int], 'bar': str | None, 'return': None}
say B(foo=[1, 2], bar='three')
say ['hello']
say ['hello', 'world']
```
