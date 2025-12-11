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

`@function(strip_final_newline) demo:bar`

```mcfunction

```

`@function demo:foo`

```mcfunction
_bolt_lineno = [1, 7], [1, 4]
_bolt_helper_children = _bolt_runtime.helpers['children']
_bolt_helper_replace = _bolt_runtime.helpers['replace']
with _bolt_runtime.scope() as _bolt_var1:
    def say_hello():
        _bolt_runtime.commands.extend(_bolt_refs[0].commands)
    _bolt_var0 = say_hello
    _bolt_var0 = _bolt_var0()
_bolt_var2 = _bolt_helper_replace(_bolt_refs[1], commands=_bolt_helper_children(_bolt_var1))
```
