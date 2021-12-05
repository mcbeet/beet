# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 7,
    "description": ""
  }
}
```

### demo

`@function demo:foo`

```mcfunction
say hello
say this is a function file augmented with mecha
execute if score @s tmp matches 1.. as @a run function demo:foo/nested_execute_0
say You can make functions
tellraw @a ["", {"text": "yep"}]
say and return values
say 13
say 21
say 34
say Unlike in python default params are evaluated when the function is called
say 12
say 144
say {'number': 12, 'result': 144}
say this is basically a custom subset of python
say functions are first-class objects just like in python
say AAA
say BBB
say CCC
say just once
execute as @a at @s if block ~ ~-1 ~ #wool run give @s stone{display: {Name: '{"text": "Hello", "bold": true}'}}
say (1, 2, 3, 4)
say (1, 2, 3, 4)
say ((1, 2, 3, 4),)
say f-strings 'WORK' too \
say {{{00000007}\}"}
execute if score @s tmp matches 8.. run say wat
execute if score @s tmp matches 8.. run say wat
```

`@function demo:foo/nested_execute_0`

```mcfunction
say multiline is automatically enabled
say nesting is automatically enabled
say implicit execute is automatically enabled
say relative location is automatically enabled
say ABCABCABCABCABC
```
