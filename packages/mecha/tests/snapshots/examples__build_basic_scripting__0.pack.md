# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 8,
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
say other
say done
say 1
say done
say 2
say done
say 3
say done
say other
say done
say other
say done
execute as @a at @s anchored eyes facing 0 0 0 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.6] run function demo:abc
execute if predicate foo:bar run function demo:xyz
execute if score @s thingy matches 0..7 run function demo:foo/0_7
execute if score @s thingy matches 8..14 run function demo:foo/8_14
execute if score @s thingy matches 15..21 run function demo:foo/15_21
execute if score @s thingy matches 22..28 run function demo:foo/22_28
execute if score @s thingy matches 29..35 run function demo:foo/29_35
data modify entity @e[type=armor_stand, limit=1] NoBasePlate set value 1b
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

`@function demo:abc`

```mcfunction
say foo
say bar
```

`@function demo:xyz`

```mcfunction
say foo
say bar
```

`@function demo:foo/0_7`

```mcfunction
execute if score @s thingy matches ..1 run function demo:foo/0_1
execute if score @s thingy matches 2..3 run function demo:foo/2_3
execute if score @s thingy matches 4..5 run function demo:foo/4_5
execute if score @s thingy matches 6 run say g
execute if score @s thingy matches 7 run say h
```

`@function demo:foo/0_1`

```mcfunction
execute if score @s thingy matches 0 run say a
execute if score @s thingy matches 1 run say b
```

`@function demo:foo/2_3`

```mcfunction
execute if score @s thingy matches 2 run say c
execute if score @s thingy matches 3 run say d
```

`@function demo:foo/4_5`

```mcfunction
execute if score @s thingy matches 4 run say e
execute if score @s thingy matches 5 run say f
```

`@function demo:foo/8_14`

```mcfunction
execute if score @s thingy matches ..9 run function demo:foo/8_9
execute if score @s thingy matches 10..11 run function demo:foo/10_11
execute if score @s thingy matches 12 run say m
execute if score @s thingy matches 13 run say n
execute if score @s thingy matches 14 run say o
```

`@function demo:foo/8_9`

```mcfunction
execute if score @s thingy matches 8 run say i
execute if score @s thingy matches 9 run say j
```

`@function demo:foo/10_11`

```mcfunction
execute if score @s thingy matches 10 run say k
execute if score @s thingy matches 11 run say l
```

`@function demo:foo/15_21`

```mcfunction
execute if score @s thingy matches ..16 run function demo:foo/15_16
execute if score @s thingy matches 17..18 run function demo:foo/17_18
execute if score @s thingy matches 19 run say t
execute if score @s thingy matches 20 run say u
execute if score @s thingy matches 21 run say v
```

`@function demo:foo/15_16`

```mcfunction
execute if score @s thingy matches 15 run say p
execute if score @s thingy matches 16 run say q
```

`@function demo:foo/17_18`

```mcfunction
execute if score @s thingy matches 17 run say r
execute if score @s thingy matches 18 run say s
```

`@function demo:foo/22_28`

```mcfunction
execute if score @s thingy matches ..23 run function demo:foo/22_23
execute if score @s thingy matches 24..25 run function demo:foo/24_25
execute if score @s thingy matches 26 run say 0
execute if score @s thingy matches 27 run say 1
execute if score @s thingy matches 28 run say 2
```

`@function demo:foo/22_23`

```mcfunction
execute if score @s thingy matches 22 run say w
execute if score @s thingy matches 23 run say x
```

`@function demo:foo/24_25`

```mcfunction
execute if score @s thingy matches 24 run say y
execute if score @s thingy matches 25 run say z
```

`@function demo:foo/29_35`

```mcfunction
execute if score @s thingy matches ..30 run function demo:foo/29_30
execute if score @s thingy matches 31..32 run function demo:foo/31_32
execute if score @s thingy matches 33 run say 7
execute if score @s thingy matches 34 run say 8
execute if score @s thingy matches 35 run say 9
```

`@function demo:foo/29_30`

```mcfunction
execute if score @s thingy matches 29 run say 3
execute if score @s thingy matches 30 run say 4
```

`@function demo:foo/31_32`

```mcfunction
execute if score @s thingy matches 31 run say 5
execute if score @s thingy matches 32 run say 6
```
