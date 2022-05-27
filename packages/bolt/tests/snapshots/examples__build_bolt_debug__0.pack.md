# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 9,
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
_mecha_lineno = [1, 7], [1, 4]
_mecha_helper_children = _mecha_runtime.helpers['children']
_mecha_helper_replace = _mecha_runtime.helpers['replace']
with _mecha_runtime.scope() as _mecha_var1:
    def say_hello():
        _mecha_runtime.commands.extend(_mecha_refs[0].commands)
    _mecha_var0 = say_hello
    _mecha_var0 = _mecha_var0()
_mecha_var2 = _mecha_helper_replace(_mecha_refs[1], commands=_mecha_helper_children(_mecha_var1))
```
