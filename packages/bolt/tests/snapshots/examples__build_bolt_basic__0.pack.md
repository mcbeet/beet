# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 12,
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
say bolt_basic.hello
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
execute if score @s thingy matches 0..7 run function demo:foo/tree_0/0_7
execute if score @s thingy matches 8..14 run function demo:foo/tree_0/8_14
execute if score @s thingy matches 15..21 run function demo:foo/tree_0/15_21
execute if score @s thingy matches 22..28 run function demo:foo/tree_0/22_28
execute if score @s thingy matches 29..35 run function demo:foo/tree_0/29_35
data modify entity @e[type=armor_stand, limit=1] NoBasePlate set value 1b
execute if score @s loop_again matches 1 run function demo:foo
setblock 1 2 3 stone
setblock 1 2 3 stone
execute if block ^ ^1 ^ #planks run say 42
execute if block ~ ~ ~ #planks run say 42
say {'foo': 1, 'bar': 2, 'thing': 42}
execute if score @s thingy matches 0..3 run function demo:foo/small_tree/0_3
execute if score @s thingy matches 4..7 run function demo:foo/small_tree/4_7
say {1: 1, 'a': 'a', 'b': 'thing', 'c': 'c', 2: 2}
say {1: {2: 'foo'}}
execute if score @s thingy matches 10..14 run function demo:foo/tree_1/10_14
execute if score @s thingy matches 15..19 run function demo:foo/tree_1/15_19
scoreboard objectives setdisplay list some_score_name
scoreboard objectives setdisplay sidebar.team.red some_score_name
item replace entity @s weapon.offhand from entity @s weapon.mainhand
item replace entity @s weapon.offhand from entity @s weapon.mainhand
say [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
say [3, 4, 5, 6, 7, 8, 9, 10, 11]
say [0, 1, 2, 3, 4, 5, 6, 7, 8]
say [3, 4, 5, 6, 7, 8]
say [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
say [3, 4, 5, 6, 7, 8, 9, 10, 11]
say [0, 1, 2, 3, 4, 5, 6, 7, 8]
say [3, 4, 5, 6, 7, 8]
say [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
say [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
say [11, 10, 9, 8, 7, 6, 5, 4]
say [9, 8, 7, 6, 5, 4]
execute at @s if block ~ ~ ~ #minecraft:beds run teleport @s ~ ~0.5625 ~
say [0, 1, 2]
say ==[a]==
say True
say None
say b
say True
say False
say foo
say ==[b]==
say True
say a
say c
say False
say False
say bar
say ==[c]==
say True
say b
say d
say False
say False
say foo
say ==[d]==
say True
say c
say None
say False
say True
say bar
say hello!!!!!
function demo:bbb
execute if data storage some:path/to/storage some.foo.path
execute if data storage some:path/to/storage some.foo.path run say hi
execute if data storage some:path/to/storage some.foo.path{my: "compound"}
execute if data storage some:path/to/storage some.foo.path{my: "compound"} run say hi
execute if data storage some:path/to/storage some.bar.path
execute if data storage some:path/to/storage some.bar.path run say hi
execute if data storage some:path/to/storage some.bar.path{my: "compound"}
execute if data storage some:path/to/storage some.bar.path{my: "compound"} run say hi
execute if data storage some:path/to/storage some.bar.path[{my: "subscript"}]
execute if data storage some:path/to/storage some.bar.path[{my: "subscript"}] run say hi
execute if data storage some:path/to/storage some.foo.path{my: "compound"}.stuff[42].beep.bar[{my: "subscript"}].boop run say hi
execute if data storage some:path/to/storage foo.bar
execute if data storage some:path/to/storage "some.foo.path"
execute if data storage some:path/to/storage something.cool[3].foo
data merge storage some:path/to/storage {Count: 23b}
execute if score some_fake_player some_objective matches 0 run say yes
execute if score 00000000-0000-0000-0000-000000000001 some_objective matches 0 run say yes
execute if score 12345678-1234-5678-1234-567812345678 some_objective matches 0 run say yes
execute at @e[type=creeper] run summon lightning_bolt
data merge storage demo:foo {custom_data1: [0, 1, 2], custom_data2: [0, 1, 2]}
setblock 0 0 0 minecraft:stone
say same thing
tellraw @a {"text": "hello world"}
execute at @s run particle minecraft:dust 0 1 1 0.9 ~ ~1 ~ 0 0 0 0.01 1 force
execute at @s run particle minecraft:block yellow_concrete ~ ~1.62 ~ 0 0.4 0 0 30 force
execute at @s run particle minecraft:block minecraft:light_blue_concrete ~ ~1 ~ 0.05 0.1 0.05 0 3
execute as @a[scores={foo=1..}] run scoreboard players remove @s foo 1
execute as @a[scores={bar=1..}] run scoreboard players remove @s bar 1
scoreboard players set @p tmp -8
setblock ~12 ~23 ~34 stone
setblock ~12 23 ~34 stone
setblock 12 23 34 stone
setblock ~12 ~23 ~34 stone
setblock ^12 ^23 ^34 stone
setblock -12 -23 -34 stone
setblock ~-12 ~-23 ~-34 stone
setblock ^-12 ^-23 ^-34 stone
say 0 a
say 1 b
say 2 c
say 1
say 2
say 3
execute if block ~ ~6 ~ air if block ~ ~5 ~ air if block ~ ~4 ~ air if block ~ ~3 ~ air if block ~ ~2 ~ air if block ~ ~1 ~ air run say nothing above!
say 0
say 1
say bolt implements a __rebind__(rhs) magic method that gets called when you reassign a value to a variable
say let's try it out by manually building a class
scoreboard players set a global 123
scoreboard players set a global 456
scoreboard players set b global 789
scoreboard players operation b global = a global
scoreboard players operation bolt_basic.tmp.0 global = b global
scoreboard players add bolt_basic.tmp.0 global 6
scoreboard players operation bolt_basic.tmp.1 global = bolt_basic.tmp.0 global
scoreboard players operation bolt_basic.tmp.1 global += a global
scoreboard players operation a global += bolt_basic.tmp.1 global
scoreboard players add b global 1
say you can use nonlocal to create fake classes
say 1
say 2
say 10
execute if score #temp abc matches 1.. run say foo
execute as @p run function #demo:yolo_funcs
say [False, False, True, False, False, False, True, False, False, False, True, False, True, True, True, True]
say hello
say hello
say hello
say hello
say thing == 1
say thing == 2
say thing == 3
say thing == 99
say thing == hello
say thing == world
execute if score @s foo matches 1 run function demo:foo/nested_execute_1
execute if score @s foo matches 0 run say no
scoreboard players operation global bolt_basic.tmp0 = global is_cool
execute unless score global is_cool matches 0 run scoreboard players operation global bolt_basic.tmp0 = global is_nice
scoreboard players operation global is_awesome = global bolt_basic.tmp0
scoreboard players set global bolt_basic.tmp1 1
execute unless score global is_awesome matches 0 run scoreboard players set global bolt_basic.tmp1 0
scoreboard players operation global bolt_basic.tmp2 = global is_awesome
execute unless score global bolt_basic.tmp1 matches 0 run scoreboard players operation global bolt_basic.tmp2 = global force_awesomeness
execute unless score global bolt_basic.tmp2 matches 0 run say hello
say this is from demo:utils
execute if data storage demo:random_data {value: 42} run say json loaded successfully
give @s bow{CustomModelData: 7}
give @s stone{CanPlaceOn: ["minecraft:dirt", "minecraft:gravel"], CustomModelData: 7}
tellraw @p ["", {"text": "hey", "color": "red"}, "minecraft:dirt", "r", "e", "d"]
say 1
say 2
say ['demo:abc', 'demo:def']
say inner dummy
say dummy
say dummy
say dummy
say AstCommand(identifier='tellraw:targets:message', arguments=AstChildren((AstSelector(variable='p', arguments=AstChildren(())), AstJsonValue(value='hello'))))
say tellraw @p "hello"
execute as 00000001-0002-0003-0405-000000000006 run function test:test
whitelist add bdd640fb-0667-1ad1-1c80-317fa3b1799d
attribute @s minecraft:generic.attack_speed modifier add 23b8c1e9-3924-56de-3eb1-3b9046685257 double 0.5 multiply
```

`@function demo:import_a`

```mcfunction
say demo:import_b
say demo:import_a
say 84
```

`@function demo:import_b`

```mcfunction
say demo:import_a
say demo:import_b
say 14
```

`@function(strip_final_newline) demo:thing`

```mcfunction

```

`@function demo:utils`

```mcfunction
say this doesn't conflict with the demo:utils module
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

`@function demo:bbb`

```mcfunction
say 0
say 1
say 2
```

`@function demo:foo/nested_execute_1`

```mcfunction
say yes
execute if score @s bar matches 1 run say with bar
```

`@function demo:foo/tree_0/0_7`

```mcfunction
execute if score @s thingy matches ..1 run function demo:foo/tree_0/0_1
execute if score @s thingy matches 2..3 run function demo:foo/tree_0/2_3
execute if score @s thingy matches 4..5 run function demo:foo/tree_0/4_5
execute if score @s thingy matches 6 run say g
execute if score @s thingy matches 7 run say h
```

`@function demo:foo/tree_0/0_1`

```mcfunction
execute if score @s thingy matches 0 run say a
execute if score @s thingy matches 1 run say b
```

`@function demo:foo/tree_0/2_3`

```mcfunction
execute if score @s thingy matches 2 run say c
execute if score @s thingy matches 3 run say d
```

`@function demo:foo/tree_0/4_5`

```mcfunction
execute if score @s thingy matches 4 run say e
execute if score @s thingy matches 5 run say f
```

`@function demo:foo/tree_0/8_14`

```mcfunction
execute if score @s thingy matches ..9 run function demo:foo/tree_0/8_9
execute if score @s thingy matches 10..11 run function demo:foo/tree_0/10_11
execute if score @s thingy matches 12 run say m
execute if score @s thingy matches 13 run say n
execute if score @s thingy matches 14 run say o
```

`@function demo:foo/tree_0/8_9`

```mcfunction
execute if score @s thingy matches 8 run say i
execute if score @s thingy matches 9 run say j
```

`@function demo:foo/tree_0/10_11`

```mcfunction
execute if score @s thingy matches 10 run say k
execute if score @s thingy matches 11 run say l
```

`@function demo:foo/tree_0/15_21`

```mcfunction
execute if score @s thingy matches ..16 run function demo:foo/tree_0/15_16
execute if score @s thingy matches 17..18 run function demo:foo/tree_0/17_18
execute if score @s thingy matches 19 run say t
execute if score @s thingy matches 20 run say u
execute if score @s thingy matches 21 run say v
```

`@function demo:foo/tree_0/15_16`

```mcfunction
execute if score @s thingy matches 15 run say p
execute if score @s thingy matches 16 run say q
```

`@function demo:foo/tree_0/17_18`

```mcfunction
execute if score @s thingy matches 17 run say r
execute if score @s thingy matches 18 run say s
```

`@function demo:foo/tree_0/22_28`

```mcfunction
execute if score @s thingy matches ..23 run function demo:foo/tree_0/22_23
execute if score @s thingy matches 24..25 run function demo:foo/tree_0/24_25
execute if score @s thingy matches 26 run say 0
execute if score @s thingy matches 27 run say 1
execute if score @s thingy matches 28 run say 2
```

`@function demo:foo/tree_0/22_23`

```mcfunction
execute if score @s thingy matches 22 run say w
execute if score @s thingy matches 23 run say x
```

`@function demo:foo/tree_0/24_25`

```mcfunction
execute if score @s thingy matches 24 run say y
execute if score @s thingy matches 25 run say z
```

`@function demo:foo/tree_0/29_35`

```mcfunction
execute if score @s thingy matches ..30 run function demo:foo/tree_0/29_30
execute if score @s thingy matches 31..32 run function demo:foo/tree_0/31_32
execute if score @s thingy matches 33 run say 7
execute if score @s thingy matches 34 run say 8
execute if score @s thingy matches 35 run say 9
```

`@function demo:foo/tree_0/29_30`

```mcfunction
execute if score @s thingy matches 29 run say 3
execute if score @s thingy matches 30 run say 4
```

`@function demo:foo/tree_0/31_32`

```mcfunction
execute if score @s thingy matches 31 run say 5
execute if score @s thingy matches 32 run say 6
```

`@function demo:foo/small_tree/0_3`

```mcfunction
execute if score @s thingy matches ..1 run function demo:foo/small_tree/0_1
execute if score @s thingy matches 2.. run function demo:foo/small_tree/2_3
```

`@function demo:foo/small_tree/0_1`

```mcfunction
execute if score @s thingy matches 0 run say 0
execute if score @s thingy matches 1 run say 1
```

`@function demo:foo/small_tree/2_3`

```mcfunction
execute if score @s thingy matches 2 run say 2
execute if score @s thingy matches 3 run say 3
```

`@function demo:foo/small_tree/4_7`

```mcfunction
execute if score @s thingy matches ..5 run function demo:foo/small_tree/4_5
execute if score @s thingy matches 6.. run function demo:foo/small_tree/6_7
```

`@function demo:foo/small_tree/4_5`

```mcfunction
execute if score @s thingy matches 4 run say 4
execute if score @s thingy matches 5 run say 5
```

`@function demo:foo/small_tree/6_7`

```mcfunction
execute if score @s thingy matches 6 run say 6
execute if score @s thingy matches 7 run say 7
```

`@function demo:foo/tree_1/10_14`

```mcfunction
execute if score @s thingy matches ..12 run function demo:foo/tree_1/10_12
execute if score @s thingy matches 13.. run function demo:foo/tree_1/13_14
```

`@function demo:foo/tree_1/10_12`

```mcfunction
execute if score @s thingy matches ..11 run function demo:foo/tree_1/10_11
execute if score @s thingy matches 12 run say 12
```

`@function demo:foo/tree_1/10_11`

```mcfunction
execute if score @s thingy matches 10 run say 10
execute if score @s thingy matches 11 run say 11
```

`@function demo:foo/tree_1/13_14`

```mcfunction
execute if score @s thingy matches 13 run say 13
execute if score @s thingy matches 14 run say 14
```

`@function demo:foo/tree_1/15_19`

```mcfunction
execute if score @s thingy matches ..17 run function demo:foo/tree_1/15_17
execute if score @s thingy matches 18.. run function demo:foo/tree_1/18_19
```

`@function demo:foo/tree_1/15_17`

```mcfunction
execute if score @s thingy matches ..16 run function demo:foo/tree_1/15_16
execute if score @s thingy matches 17 run say 17
```

`@function demo:foo/tree_1/15_16`

```mcfunction
execute if score @s thingy matches 15 run say 15
execute if score @s thingy matches 16 run say 16
```

`@function demo:foo/tree_1/18_19`

```mcfunction
execute if score @s thingy matches 18 run say 18
execute if score @s thingy matches 19 run say 19
```

`@function demo:no_quotes_lol`

```mcfunction
say that's neat
```

`@function_tag demo:yolo_funcs`

```json
{
  "values": [
    "demo:foo"
  ]
}
```

`@predicate demo:check_scores`

```json
[
  {
    "condition": "minecraft:entity_scores",
    "entity": "this",
    "scores": {
      "foo": 1
    }
  },
  {
    "condition": "minecraft:entity_scores",
    "entity": "killer_player",
    "scores": {
      "bar": 1
    }
  }
]
```

### felix

`@function_tag felix:howdy`

```json
{
  "values": [
    "demo:foo",
    "demo:foo"
  ]
}
```

### minecraft

`@function_tag minecraft:load`

```json
{
  "values": [
    "bolt_basic:load_storage"
  ]
}
```

### bolt_basic

`@function bolt_basic:load_storage`

```mcfunction
data merge storage demo:random_data {value: 42}
say json loaded!
```

## Resource pack

`@resource_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 13,
    "description": ""
  }
}
```

### minecraft

`@language minecraft:aaaa`

```json
{
  "menu.singleplayer": "AAAA",
  "something.else": "bonjour",
  "yaml.key1": "BONJOUR",
  "yaml.key2": "Bonjour"
}
```

`@particle minecraft:end_rod`

```json
{
  "textures": [
    "minecraft:glitter_7",
    "minecraft:glitter_6",
    "minecraft:glitter_5",
    "minecraft:glitter_4",
    "minecraft:glitter_3",
    "minecraft:glitter_2",
    "minecraft:glitter_1",
    "minecraft:glitter_0"
  ]
}
```
