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
item replace entity @a hotbar.0 from entity @s hotbar.0
item replace entity @a hotbar.1 from entity @s hotbar.1
item replace entity @a hotbar.2 from entity @s hotbar.2
item replace entity @a hotbar.3 from entity @s hotbar.3
item replace entity @a hotbar.4 from entity @s hotbar.4
item replace entity @a hotbar.5 from entity @s hotbar.5
item replace entity @a hotbar.6 from entity @s hotbar.6
item replace entity @a hotbar.7 from entity @s hotbar.7
item replace entity @a hotbar.8 from entity @s hotbar.8
item replace entity @a inventory.0 from entity @s inventory.0
item replace entity @a inventory.1 from entity @s inventory.1
item replace entity @a inventory.2 from entity @s inventory.2
item replace entity @a inventory.3 from entity @s inventory.3
item replace entity @a inventory.4 from entity @s inventory.4
item replace entity @a inventory.5 from entity @s inventory.5
item replace entity @a inventory.6 from entity @s inventory.6
item replace entity @a inventory.7 from entity @s inventory.7
item replace entity @a inventory.8 from entity @s inventory.8
item replace entity @a inventory.9 from entity @s inventory.9
item replace entity @a inventory.10 from entity @s inventory.10
item replace entity @a inventory.11 from entity @s inventory.11
item replace entity @a inventory.12 from entity @s inventory.12
item replace entity @a inventory.13 from entity @s inventory.13
item replace entity @a inventory.14 from entity @s inventory.14
item replace entity @a inventory.15 from entity @s inventory.15
item replace entity @a inventory.16 from entity @s inventory.16
item replace entity @a inventory.17 from entity @s inventory.17
item replace entity @a inventory.18 from entity @s inventory.18
item replace entity @a inventory.19 from entity @s inventory.19
item replace entity @a inventory.20 from entity @s inventory.20
item replace entity @a inventory.21 from entity @s inventory.21
item replace entity @a inventory.22 from entity @s inventory.22
item replace entity @a inventory.23 from entity @s inventory.23
item replace entity @a inventory.24 from entity @s inventory.24
item replace entity @a inventory.25 from entity @s inventory.25
say 1
say 2
say 3
say [1, 2, 3, 1, 2, 3]
say basic_scripting.hello
say -1.0
say True
say 0.0
say True
```

`@function(strip_final_newline) demo:thing`

```mcfunction

```

`@function demo:foo/nested_execute_0`

```mcfunction
say multiline is automatically enabled
say nesting is automatically enabled
say implicit execute is automatically enabled
say relative location is automatically enabled
say ABCABCABCABCABC
```
