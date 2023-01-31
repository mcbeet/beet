# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 10,
    "description": ""
  }
}
```

### demo

`@function demo:ref/bar`

```mcfunction
execute as @a run function demo:ref/bar/nested_execute_0
execute as @e[type=pig, scores={foo=1.., bar=0}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 0
execute as @e[type=pig, scores={foo=1.., bar=0}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~ air
execute as @e[type=pig, scores={foo=1.., bar=1}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 1
execute as @e[type=pig, scores={foo=1.., bar=1}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~1 air
execute as @e[type=pig, scores={foo=1.., bar=2}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 2
execute as @e[type=pig, scores={foo=1.., bar=2}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~2 air
execute as @e[type=pig, scores={foo=1.., bar=3}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 3
execute as @e[type=pig, scores={foo=1.., bar=3}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~3 air
execute as @e[type=pig, scores={foo=1.., bar=4}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 4
execute as @e[type=pig, scores={foo=1.., bar=4}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~4 air
execute as @e[type=pig, scores={foo=1.., bar=5}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 5
execute as @e[type=pig, scores={foo=1.., bar=5}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~5 air
execute as @e[type=pig, scores={foo=1.., bar=6}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 6
execute as @e[type=pig, scores={foo=1.., bar=6}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~6 air
execute as @e[type=pig, scores={foo=1.., bar=7}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 7
execute as @e[type=pig, scores={foo=1.., bar=7}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~7 air
execute as @e[type=pig, scores={foo=1.., bar=8}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 8
execute as @e[type=pig, scores={foo=1.., bar=8}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~8 air
execute as @e[type=pig, scores={foo=1.., bar=9}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 9
execute as @e[type=pig, scores={foo=1.., bar=9}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~9 air
execute as @e[type=pig, scores={foo=1.., bar=10}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 10
execute as @e[type=pig, scores={foo=1.., bar=10}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~10 air
execute as @e[type=pig, scores={foo=1.., bar=11}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 11
execute as @e[type=pig, scores={foo=1.., bar=11}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~11 air
execute as @e[type=pig, scores={foo=1.., bar=12}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 12
execute as @e[type=pig, scores={foo=1.., bar=12}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~12 air
execute as @e[type=pig, scores={foo=1.., bar=13}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 13
execute as @e[type=pig, scores={foo=1.., bar=13}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~13 air
execute as @e[type=pig, scores={foo=1.., bar=14}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 14
execute as @e[type=pig, scores={foo=1.., bar=14}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~14 air
execute as @e[type=pig, scores={foo=1.., bar=15}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 15
execute as @e[type=pig, scores={foo=1.., bar=15}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~15 air
execute as @e[type=pig, scores={foo=1.., bar=16}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 16
execute as @e[type=pig, scores={foo=1.., bar=16}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~16 air
execute as @e[type=pig, scores={foo=1.., bar=17}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 17
execute as @e[type=pig, scores={foo=1.., bar=17}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~17 air
execute as @e[type=pig, scores={foo=1.., bar=18}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 18
execute as @e[type=pig, scores={foo=1.., bar=18}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~18 air
execute as @e[type=pig, scores={foo=1.., bar=19}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 19
execute as @e[type=pig, scores={foo=1.., bar=19}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~19 air
execute as @e[type=pig, scores={foo=1.., bar=20}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 20
execute as @e[type=pig, scores={foo=1.., bar=20}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~20 air
execute as @e[type=pig, scores={foo=1.., bar=21}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 21
execute as @e[type=pig, scores={foo=1.., bar=21}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~21 air
execute as @e[type=pig, scores={foo=1.., bar=22}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 22
execute as @e[type=pig, scores={foo=1.., bar=22}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~22 air
execute as @e[type=pig, scores={foo=1.., bar=23}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 23
execute as @e[type=pig, scores={foo=1.., bar=23}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~23 air
execute as @e[type=pig, scores={foo=1.., bar=24}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 24
execute as @e[type=pig, scores={foo=1.., bar=24}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~24 air
execute as @e[type=pig, scores={foo=1.., bar=25}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 25
execute as @e[type=pig, scores={foo=1.., bar=25}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~25 air
execute as @e[type=pig, scores={foo=1.., bar=26}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 26
execute as @e[type=pig, scores={foo=1.., bar=26}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~26 air
execute as @e[type=pig, scores={foo=1.., bar=27}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 27
execute as @e[type=pig, scores={foo=1.., bar=27}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~27 air
execute as @e[type=pig, scores={foo=1.., bar=28}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 28
execute as @e[type=pig, scores={foo=1.., bar=28}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~28 air
execute as @e[type=pig, scores={foo=1.., bar=29}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 29
execute as @e[type=pig, scores={foo=1.., bar=29}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~29 air
execute as @e[type=pig, scores={foo=1.., bar=30}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 30
execute as @e[type=pig, scores={foo=1.., bar=30}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~30 air
execute as @e[type=pig, scores={foo=1.., bar=31}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 31
execute as @e[type=pig, scores={foo=1.., bar=31}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~31 air
execute as @e[type=pig, scores={foo=1.., bar=32}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 32
execute as @e[type=pig, scores={foo=1.., bar=32}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~32 air
execute as @e[type=pig, scores={foo=1.., bar=33}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 33
execute as @e[type=pig, scores={foo=1.., bar=33}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~33 air
execute as @e[type=pig, scores={foo=1.., bar=34}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 34
execute as @e[type=pig, scores={foo=1.., bar=34}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~34 air
execute as @e[type=pig, scores={foo=1.., bar=35}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 35
execute as @e[type=pig, scores={foo=1.., bar=35}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~35 air
execute as @e[type=pig, scores={foo=1.., bar=36}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 36
execute as @e[type=pig, scores={foo=1.., bar=36}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~36 air
execute as @e[type=pig, scores={foo=1.., bar=37}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 37
execute as @e[type=pig, scores={foo=1.., bar=37}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~37 air
execute as @e[type=pig, scores={foo=1.., bar=38}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 38
execute as @e[type=pig, scores={foo=1.., bar=38}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~38 air
execute as @e[type=pig, scores={foo=1.., bar=39}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 39
execute as @e[type=pig, scores={foo=1.., bar=39}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~39 air
execute as @e[type=pig, scores={foo=1.., bar=40}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 40
execute as @e[type=pig, scores={foo=1.., bar=40}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~40 air
execute as @e[type=pig, scores={foo=1.., bar=41}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 41
execute as @e[type=pig, scores={foo=1.., bar=41}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~41 air
execute if score @s thingy matches 0..20 run function demo:ref/bar/tree_42/0_20
execute if score @s thingy matches 21..41 run function demo:ref/bar/tree_42/21_41
say ok
say bye
execute if score @s thingy matches 0..20 run function demo:ref/bar/tree_42/0_20
execute if score @s thingy matches 21..41 run function demo:ref/bar/tree_42/21_41
execute if score @s thingy matches 0..28 run function demo:ref/bar/tree_57/0_28
execute if score @s thingy matches 29..56 run function demo:ref/bar/tree_57/29_56
```

`@function demo:ref/foo`

```mcfunction
say 123
say (((1, 2), (1, 2)), ((1, 2), (1, 2)))
say wat
```

`@function demo:ref/bar/tree_42/0_20`

```mcfunction
execute if score @s thingy matches ..10 run function demo:ref/bar/tree_42/0_10
execute if score @s thingy matches 11.. run function demo:ref/bar/tree_42/11_20
```

`@function demo:ref/bar/tree_42/0_10`

```mcfunction
execute if score @s thingy matches ..5 run function demo:ref/bar/tree_42/0_5
execute if score @s thingy matches 6.. run function demo:ref/bar/tree_42/6_10
```

`@function demo:ref/bar/tree_42/0_5`

```mcfunction
execute if score @s thingy matches ..2 run function demo:ref/bar/tree_42/0_2
execute if score @s thingy matches 3.. run function demo:ref/bar/tree_42/3_5
```

`@function demo:ref/bar/tree_42/0_2`

```mcfunction
execute if score @s thingy matches ..1 run function demo:ref/bar/tree_42/0_1
execute if score @s thingy matches 2 run say 2
```

`@function demo:ref/bar/tree_42/0_1`

```mcfunction
execute if score @s thingy matches 0 run say 0
execute if score @s thingy matches 1 run say 1
```

`@function demo:ref/bar/tree_42/3_5`

```mcfunction
execute if score @s thingy matches ..4 run function demo:ref/bar/tree_42/3_4
execute if score @s thingy matches 5 run say 5
```

`@function demo:ref/bar/tree_42/3_4`

```mcfunction
execute if score @s thingy matches 3 run say 3
execute if score @s thingy matches 4 run say 4
```

`@function demo:ref/bar/tree_42/6_10`

```mcfunction
execute if score @s thingy matches ..8 run function demo:ref/bar/tree_42/6_8
execute if score @s thingy matches 9.. run function demo:ref/bar/tree_42/9_10
```

`@function demo:ref/bar/tree_42/6_8`

```mcfunction
execute if score @s thingy matches ..7 run function demo:ref/bar/tree_42/6_7
execute if score @s thingy matches 8 run say 8
```

`@function demo:ref/bar/tree_42/6_7`

```mcfunction
execute if score @s thingy matches 6 run say 6
execute if score @s thingy matches 7 run say 7
```

`@function demo:ref/bar/tree_42/9_10`

```mcfunction
execute if score @s thingy matches 9 run say 9
execute if score @s thingy matches 10 run say 10
```

`@function demo:ref/bar/tree_42/11_20`

```mcfunction
execute if score @s thingy matches ..15 run function demo:ref/bar/tree_42/11_15
execute if score @s thingy matches 16.. run function demo:ref/bar/tree_42/16_20
```

`@function demo:ref/bar/tree_42/11_15`

```mcfunction
execute if score @s thingy matches ..13 run function demo:ref/bar/tree_42/11_13
execute if score @s thingy matches 14.. run function demo:ref/bar/tree_42/14_15
```

`@function demo:ref/bar/tree_42/11_13`

```mcfunction
execute if score @s thingy matches ..12 run function demo:ref/bar/tree_42/11_12
execute if score @s thingy matches 13 run say 13
```

`@function demo:ref/bar/tree_42/11_12`

```mcfunction
execute if score @s thingy matches 11 run say 11
execute if score @s thingy matches 12 run say 12
```

`@function demo:ref/bar/tree_42/14_15`

```mcfunction
execute if score @s thingy matches 14 run say 14
execute if score @s thingy matches 15 run say 15
```

`@function demo:ref/bar/tree_42/16_20`

```mcfunction
execute if score @s thingy matches ..18 run function demo:ref/bar/tree_42/16_18
execute if score @s thingy matches 19.. run function demo:ref/bar/tree_42/19_20
```

`@function demo:ref/bar/tree_42/16_18`

```mcfunction
execute if score @s thingy matches ..17 run function demo:ref/bar/tree_42/16_17
execute if score @s thingy matches 18 run say 18
```

`@function demo:ref/bar/tree_42/16_17`

```mcfunction
execute if score @s thingy matches 16 run say 16
execute if score @s thingy matches 17 run say 17
```

`@function demo:ref/bar/tree_42/19_20`

```mcfunction
execute if score @s thingy matches 19 run say 19
execute if score @s thingy matches 20 run say 20
```

`@function demo:ref/bar/tree_42/21_41`

```mcfunction
execute if score @s thingy matches ..31 run function demo:ref/bar/tree_42/21_31
execute if score @s thingy matches 32.. run function demo:ref/bar/tree_42/32_41
```

`@function demo:ref/bar/tree_42/21_31`

```mcfunction
execute if score @s thingy matches ..26 run function demo:ref/bar/tree_42/21_26
execute if score @s thingy matches 27.. run function demo:ref/bar/tree_42/27_31
```

`@function demo:ref/bar/tree_42/21_26`

```mcfunction
execute if score @s thingy matches ..23 run function demo:ref/bar/tree_42/21_23
execute if score @s thingy matches 24.. run function demo:ref/bar/tree_42/24_26
```

`@function demo:ref/bar/tree_42/21_23`

```mcfunction
execute if score @s thingy matches ..22 run function demo:ref/bar/tree_42/21_22
execute if score @s thingy matches 23 run say 23
```

`@function demo:ref/bar/tree_42/21_22`

```mcfunction
execute if score @s thingy matches 21 run say 21
execute if score @s thingy matches 22 run say 22
```

`@function demo:ref/bar/tree_42/24_26`

```mcfunction
execute if score @s thingy matches ..25 run function demo:ref/bar/tree_42/24_25
execute if score @s thingy matches 26 run say 26
```

`@function demo:ref/bar/tree_42/24_25`

```mcfunction
execute if score @s thingy matches 24 run say 24
execute if score @s thingy matches 25 run say 25
```

`@function demo:ref/bar/tree_42/27_31`

```mcfunction
execute if score @s thingy matches ..29 run function demo:ref/bar/tree_42/27_29
execute if score @s thingy matches 30.. run function demo:ref/bar/tree_42/30_31
```

`@function demo:ref/bar/tree_42/27_29`

```mcfunction
execute if score @s thingy matches ..28 run function demo:ref/bar/tree_42/27_28
execute if score @s thingy matches 29 run say 29
```

`@function demo:ref/bar/tree_42/27_28`

```mcfunction
execute if score @s thingy matches 27 run say 27
execute if score @s thingy matches 28 run say 28
```

`@function demo:ref/bar/tree_42/30_31`

```mcfunction
execute if score @s thingy matches 30 run say 30
execute if score @s thingy matches 31 run say 31
```

`@function demo:ref/bar/tree_42/32_41`

```mcfunction
execute if score @s thingy matches ..36 run function demo:ref/bar/tree_42/32_36
execute if score @s thingy matches 37.. run function demo:ref/bar/tree_42/37_41
```

`@function demo:ref/bar/tree_42/32_36`

```mcfunction
execute if score @s thingy matches ..34 run function demo:ref/bar/tree_42/32_34
execute if score @s thingy matches 35.. run function demo:ref/bar/tree_42/35_36
```

`@function demo:ref/bar/tree_42/32_34`

```mcfunction
execute if score @s thingy matches ..33 run function demo:ref/bar/tree_42/32_33
execute if score @s thingy matches 34 run say 34
```

`@function demo:ref/bar/tree_42/32_33`

```mcfunction
execute if score @s thingy matches 32 run say 32
execute if score @s thingy matches 33 run say 33
```

`@function demo:ref/bar/tree_42/35_36`

```mcfunction
execute if score @s thingy matches 35 run say 35
execute if score @s thingy matches 36 run say 36
```

`@function demo:ref/bar/tree_42/37_41`

```mcfunction
execute if score @s thingy matches ..39 run function demo:ref/bar/tree_42/37_39
execute if score @s thingy matches 40.. run function demo:ref/bar/tree_42/40_41
```

`@function demo:ref/bar/tree_42/37_39`

```mcfunction
execute if score @s thingy matches ..38 run function demo:ref/bar/tree_42/37_38
execute if score @s thingy matches 39 run say 39
```

`@function demo:ref/bar/tree_42/37_38`

```mcfunction
execute if score @s thingy matches 37 run say 37
execute if score @s thingy matches 38 run say 38
```

`@function demo:ref/bar/tree_42/40_41`

```mcfunction
execute if score @s thingy matches 40 run say 40
execute if score @s thingy matches 41 run say 41
```

`@function demo:ref/bar/tree_57/0_28`

```mcfunction
execute if score @s thingy matches ..14 run function demo:ref/bar/tree_57/0_14
execute if score @s thingy matches 15.. run function demo:ref/bar/tree_57/15_28
```

`@function demo:ref/bar/tree_57/0_14`

```mcfunction
execute if score @s thingy matches ..7 run function demo:ref/bar/tree_57/0_7
execute if score @s thingy matches 8.. run function demo:ref/bar/tree_57/8_14
```

`@function demo:ref/bar/tree_57/0_7`

```mcfunction
execute if score @s thingy matches ..3 run function demo:ref/bar/tree_57/0_3
execute if score @s thingy matches 4.. run function demo:ref/bar/tree_57/4_7
```

`@function demo:ref/bar/tree_57/0_3`

```mcfunction
execute if score @s thingy matches ..1 run function demo:ref/bar/tree_57/0_1
execute if score @s thingy matches 2.. run function demo:ref/bar/tree_57/2_3
```

`@function demo:ref/bar/tree_57/0_1`

```mcfunction
execute if score @s thingy matches 0 run say 0
execute if score @s thingy matches 1 run say 1
```

`@function demo:ref/bar/tree_57/2_3`

```mcfunction
execute if score @s thingy matches 2 run say 2
execute if score @s thingy matches 3 run say 3
```

`@function demo:ref/bar/tree_57/4_7`

```mcfunction
execute if score @s thingy matches ..5 run function demo:ref/bar/tree_57/4_5
execute if score @s thingy matches 6.. run function demo:ref/bar/tree_57/6_7
```

`@function demo:ref/bar/tree_57/4_5`

```mcfunction
execute if score @s thingy matches 4 run say 4
execute if score @s thingy matches 5 run say 5
```

`@function demo:ref/bar/tree_57/6_7`

```mcfunction
execute if score @s thingy matches 6 run say 6
execute if score @s thingy matches 7 run say 7
```

`@function demo:ref/bar/tree_57/8_14`

```mcfunction
execute if score @s thingy matches ..11 run function demo:ref/bar/tree_57/8_11
execute if score @s thingy matches 12.. run function demo:ref/bar/tree_57/12_14
```

`@function demo:ref/bar/tree_57/8_11`

```mcfunction
execute if score @s thingy matches ..9 run function demo:ref/bar/tree_57/8_9
execute if score @s thingy matches 10.. run function demo:ref/bar/tree_57/10_11
```

`@function demo:ref/bar/tree_57/8_9`

```mcfunction
execute if score @s thingy matches 8 run say 8
execute if score @s thingy matches 9 run say 9
```

`@function demo:ref/bar/tree_57/10_11`

```mcfunction
execute if score @s thingy matches 10 run say 10
execute if score @s thingy matches 11 run say 11
```

`@function demo:ref/bar/tree_57/12_14`

```mcfunction
execute if score @s thingy matches ..13 run function demo:ref/bar/tree_57/12_13
execute if score @s thingy matches 14 run say 14
```

`@function demo:ref/bar/tree_57/12_13`

```mcfunction
execute if score @s thingy matches 12 run say 12
execute if score @s thingy matches 13 run say 13
```

`@function demo:ref/bar/tree_57/15_28`

```mcfunction
execute if score @s thingy matches ..21 run function demo:ref/bar/tree_57/15_21
execute if score @s thingy matches 22.. run function demo:ref/bar/tree_57/22_28
```

`@function demo:ref/bar/tree_57/15_21`

```mcfunction
execute if score @s thingy matches ..18 run function demo:ref/bar/tree_57/15_18
execute if score @s thingy matches 19.. run function demo:ref/bar/tree_57/19_21
```

`@function demo:ref/bar/tree_57/15_18`

```mcfunction
execute if score @s thingy matches ..16 run function demo:ref/bar/tree_57/15_16
execute if score @s thingy matches 17.. run function demo:ref/bar/tree_57/17_18
```

`@function demo:ref/bar/tree_57/15_16`

```mcfunction
execute if score @s thingy matches 15 run say 15
execute if score @s thingy matches 16 run say 16
```

`@function demo:ref/bar/tree_57/17_18`

```mcfunction
execute if score @s thingy matches 17 run say 17
execute if score @s thingy matches 18 run say 18
```

`@function demo:ref/bar/tree_57/19_21`

```mcfunction
execute if score @s thingy matches ..20 run function demo:ref/bar/tree_57/19_20
execute if score @s thingy matches 21 run say 21
```

`@function demo:ref/bar/tree_57/19_20`

```mcfunction
execute if score @s thingy matches 19 run say 19
execute if score @s thingy matches 20 run say 20
```

`@function demo:ref/bar/tree_57/22_28`

```mcfunction
execute if score @s thingy matches ..25 run function demo:ref/bar/tree_57/22_25
execute if score @s thingy matches 26.. run function demo:ref/bar/tree_57/26_28
```

`@function demo:ref/bar/tree_57/22_25`

```mcfunction
execute if score @s thingy matches ..23 run function demo:ref/bar/tree_57/22_23
execute if score @s thingy matches 24.. run function demo:ref/bar/tree_57/24_25
```

`@function demo:ref/bar/tree_57/22_23`

```mcfunction
execute if score @s thingy matches 22 run say 22
execute if score @s thingy matches 23 run say 23
```

`@function demo:ref/bar/tree_57/24_25`

```mcfunction
execute if score @s thingy matches 24 run say 24
execute if score @s thingy matches 25 run say 25
```

`@function demo:ref/bar/tree_57/26_28`

```mcfunction
execute if score @s thingy matches ..27 run function demo:ref/bar/tree_57/26_27
execute if score @s thingy matches 28 run say 28
```

`@function demo:ref/bar/tree_57/26_27`

```mcfunction
execute if score @s thingy matches 26 run say 26
execute if score @s thingy matches 27 run say 27
```

`@function demo:ref/bar/tree_57/29_56`

```mcfunction
execute if score @s thingy matches ..42 run function demo:ref/bar/tree_57/29_42
execute if score @s thingy matches 43.. run function demo:ref/bar/tree_57/43_56
```

`@function demo:ref/bar/tree_57/29_42`

```mcfunction
execute if score @s thingy matches ..35 run function demo:ref/bar/tree_57/29_35
execute if score @s thingy matches 36.. run function demo:ref/bar/tree_57/36_42
```

`@function demo:ref/bar/tree_57/29_35`

```mcfunction
execute if score @s thingy matches ..32 run function demo:ref/bar/tree_57/29_32
execute if score @s thingy matches 33.. run function demo:ref/bar/tree_57/33_35
```

`@function demo:ref/bar/tree_57/29_32`

```mcfunction
execute if score @s thingy matches ..30 run function demo:ref/bar/tree_57/29_30
execute if score @s thingy matches 31.. run function demo:ref/bar/tree_57/31_32
```

`@function demo:ref/bar/tree_57/29_30`

```mcfunction
execute if score @s thingy matches 29 run say 29
execute if score @s thingy matches 30 run say 30
```

`@function demo:ref/bar/tree_57/31_32`

```mcfunction
execute if score @s thingy matches 31 run say 31
execute if score @s thingy matches 32 run say 32
```

`@function demo:ref/bar/tree_57/33_35`

```mcfunction
execute if score @s thingy matches ..34 run function demo:ref/bar/tree_57/33_34
execute if score @s thingy matches 35 run say 35
```

`@function demo:ref/bar/tree_57/33_34`

```mcfunction
execute if score @s thingy matches 33 run say 33
execute if score @s thingy matches 34 run say 34
```

`@function demo:ref/bar/tree_57/36_42`

```mcfunction
execute if score @s thingy matches ..39 run function demo:ref/bar/tree_57/36_39
execute if score @s thingy matches 40.. run function demo:ref/bar/tree_57/40_42
```

`@function demo:ref/bar/tree_57/36_39`

```mcfunction
execute if score @s thingy matches ..37 run function demo:ref/bar/tree_57/36_37
execute if score @s thingy matches 38.. run function demo:ref/bar/tree_57/38_39
```

`@function demo:ref/bar/tree_57/36_37`

```mcfunction
execute if score @s thingy matches 36 run say 36
execute if score @s thingy matches 37 run say 37
```

`@function demo:ref/bar/tree_57/38_39`

```mcfunction
execute if score @s thingy matches 38 run say 38
execute if score @s thingy matches 39 run say 39
```

`@function demo:ref/bar/tree_57/40_42`

```mcfunction
execute if score @s thingy matches ..41 run function demo:ref/bar/tree_57/40_41
execute if score @s thingy matches 42 run say 42
```

`@function demo:ref/bar/tree_57/40_41`

```mcfunction
execute if score @s thingy matches 40 run say 40
execute if score @s thingy matches 41 run say 41
```

`@function demo:ref/bar/tree_57/43_56`

```mcfunction
execute if score @s thingy matches ..49 run function demo:ref/bar/tree_57/43_49
execute if score @s thingy matches 50.. run function demo:ref/bar/tree_57/50_56
```

`@function demo:ref/bar/tree_57/43_49`

```mcfunction
execute if score @s thingy matches ..46 run function demo:ref/bar/tree_57/43_46
execute if score @s thingy matches 47.. run function demo:ref/bar/tree_57/47_49
```

`@function demo:ref/bar/tree_57/43_46`

```mcfunction
execute if score @s thingy matches ..44 run function demo:ref/bar/tree_57/43_44
execute if score @s thingy matches 45.. run function demo:ref/bar/tree_57/45_46
```

`@function demo:ref/bar/tree_57/43_44`

```mcfunction
execute if score @s thingy matches 43 run say 43
execute if score @s thingy matches 44 run say 44
```

`@function demo:ref/bar/tree_57/45_46`

```mcfunction
execute if score @s thingy matches 45 run say 45
execute if score @s thingy matches 46 run say 46
```

`@function demo:ref/bar/tree_57/47_49`

```mcfunction
execute if score @s thingy matches ..48 run function demo:ref/bar/tree_57/47_48
execute if score @s thingy matches 49 run say 49
```

`@function demo:ref/bar/tree_57/47_48`

```mcfunction
execute if score @s thingy matches 47 run say 47
execute if score @s thingy matches 48 run say 48
```

`@function demo:ref/bar/tree_57/50_56`

```mcfunction
execute if score @s thingy matches ..53 run function demo:ref/bar/tree_57/50_53
execute if score @s thingy matches 54.. run function demo:ref/bar/tree_57/54_56
```

`@function demo:ref/bar/tree_57/50_53`

```mcfunction
execute if score @s thingy matches ..51 run function demo:ref/bar/tree_57/50_51
execute if score @s thingy matches 52.. run function demo:ref/bar/tree_57/52_53
```

`@function demo:ref/bar/tree_57/50_51`

```mcfunction
execute if score @s thingy matches 50 run say 50
execute if score @s thingy matches 51 run say 51
```

`@function demo:ref/bar/tree_57/52_53`

```mcfunction
execute if score @s thingy matches 52 run say 52
execute if score @s thingy matches 53 run say 53
```

`@function demo:ref/bar/tree_57/54_56`

```mcfunction
execute if score @s thingy matches ..55 run function demo:ref/bar/tree_57/54_55
execute if score @s thingy matches 56 run say 56
```

`@function demo:ref/bar/tree_57/54_55`

```mcfunction
execute if score @s thingy matches 54 run say 54
execute if score @s thingy matches 55 run say 55
```

`@function demo:ref/ayy`

```mcfunction
say 123
```

`@function demo:ref/bar/nested_execute_0`

```mcfunction
say hello
```

`@function demo:bar`

```mcfunction
execute as @a run function demo:bar/nested_execute_0
execute as @e[type=pig, scores={foo=1.., bar=0}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 0
execute as @e[type=pig, scores={foo=1.., bar=0}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~ air
execute as @e[type=pig, scores={foo=1.., bar=1}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 1
execute as @e[type=pig, scores={foo=1.., bar=1}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~1 air
execute as @e[type=pig, scores={foo=1.., bar=2}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 2
execute as @e[type=pig, scores={foo=1.., bar=2}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~2 air
execute as @e[type=pig, scores={foo=1.., bar=3}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 3
execute as @e[type=pig, scores={foo=1.., bar=3}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~3 air
execute as @e[type=pig, scores={foo=1.., bar=4}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 4
execute as @e[type=pig, scores={foo=1.., bar=4}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~4 air
execute as @e[type=pig, scores={foo=1.., bar=5}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 5
execute as @e[type=pig, scores={foo=1.., bar=5}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~5 air
execute as @e[type=pig, scores={foo=1.., bar=6}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 6
execute as @e[type=pig, scores={foo=1.., bar=6}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~6 air
execute as @e[type=pig, scores={foo=1.., bar=7}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 7
execute as @e[type=pig, scores={foo=1.., bar=7}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~7 air
execute as @e[type=pig, scores={foo=1.., bar=8}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 8
execute as @e[type=pig, scores={foo=1.., bar=8}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~8 air
execute as @e[type=pig, scores={foo=1.., bar=9}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 9
execute as @e[type=pig, scores={foo=1.., bar=9}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~9 air
execute as @e[type=pig, scores={foo=1.., bar=10}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 10
execute as @e[type=pig, scores={foo=1.., bar=10}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~10 air
execute as @e[type=pig, scores={foo=1.., bar=11}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 11
execute as @e[type=pig, scores={foo=1.., bar=11}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~11 air
execute as @e[type=pig, scores={foo=1.., bar=12}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 12
execute as @e[type=pig, scores={foo=1.., bar=12}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~12 air
execute as @e[type=pig, scores={foo=1.., bar=13}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 13
execute as @e[type=pig, scores={foo=1.., bar=13}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~13 air
execute as @e[type=pig, scores={foo=1.., bar=14}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 14
execute as @e[type=pig, scores={foo=1.., bar=14}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~14 air
execute as @e[type=pig, scores={foo=1.., bar=15}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 15
execute as @e[type=pig, scores={foo=1.., bar=15}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~15 air
execute as @e[type=pig, scores={foo=1.., bar=16}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 16
execute as @e[type=pig, scores={foo=1.., bar=16}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~16 air
execute as @e[type=pig, scores={foo=1.., bar=17}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 17
execute as @e[type=pig, scores={foo=1.., bar=17}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~17 air
execute as @e[type=pig, scores={foo=1.., bar=18}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 18
execute as @e[type=pig, scores={foo=1.., bar=18}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~18 air
execute as @e[type=pig, scores={foo=1.., bar=19}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 19
execute as @e[type=pig, scores={foo=1.., bar=19}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~19 air
execute as @e[type=pig, scores={foo=1.., bar=20}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 20
execute as @e[type=pig, scores={foo=1.., bar=20}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~20 air
execute as @e[type=pig, scores={foo=1.., bar=21}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 21
execute as @e[type=pig, scores={foo=1.., bar=21}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~21 air
execute as @e[type=pig, scores={foo=1.., bar=22}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 22
execute as @e[type=pig, scores={foo=1.., bar=22}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~22 air
execute as @e[type=pig, scores={foo=1.., bar=23}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 23
execute as @e[type=pig, scores={foo=1.., bar=23}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~23 air
execute as @e[type=pig, scores={foo=1.., bar=24}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 24
execute as @e[type=pig, scores={foo=1.., bar=24}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~24 air
execute as @e[type=pig, scores={foo=1.., bar=25}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 25
execute as @e[type=pig, scores={foo=1.., bar=25}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~25 air
execute as @e[type=pig, scores={foo=1.., bar=26}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 26
execute as @e[type=pig, scores={foo=1.., bar=26}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~26 air
execute as @e[type=pig, scores={foo=1.., bar=27}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 27
execute as @e[type=pig, scores={foo=1.., bar=27}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~27 air
execute as @e[type=pig, scores={foo=1.., bar=28}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 28
execute as @e[type=pig, scores={foo=1.., bar=28}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~28 air
execute as @e[type=pig, scores={foo=1.., bar=29}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 29
execute as @e[type=pig, scores={foo=1.., bar=29}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~29 air
execute as @e[type=pig, scores={foo=1.., bar=30}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 30
execute as @e[type=pig, scores={foo=1.., bar=30}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~30 air
execute as @e[type=pig, scores={foo=1.., bar=31}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 31
execute as @e[type=pig, scores={foo=1.., bar=31}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~31 air
execute as @e[type=pig, scores={foo=1.., bar=32}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 32
execute as @e[type=pig, scores={foo=1.., bar=32}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~32 air
execute as @e[type=pig, scores={foo=1.., bar=33}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 33
execute as @e[type=pig, scores={foo=1.., bar=33}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~33 air
execute as @e[type=pig, scores={foo=1.., bar=34}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 34
execute as @e[type=pig, scores={foo=1.., bar=34}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~34 air
execute as @e[type=pig, scores={foo=1.., bar=35}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 35
execute as @e[type=pig, scores={foo=1.., bar=35}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~35 air
execute as @e[type=pig, scores={foo=1.., bar=36}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 36
execute as @e[type=pig, scores={foo=1.., bar=36}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~36 air
execute as @e[type=pig, scores={foo=1.., bar=37}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 37
execute as @e[type=pig, scores={foo=1.., bar=37}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~37 air
execute as @e[type=pig, scores={foo=1.., bar=38}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 38
execute as @e[type=pig, scores={foo=1.., bar=38}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~38 air
execute as @e[type=pig, scores={foo=1.., bar=39}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 39
execute as @e[type=pig, scores={foo=1.., bar=39}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~39 air
execute as @e[type=pig, scores={foo=1.., bar=40}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 40
execute as @e[type=pig, scores={foo=1.., bar=40}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~40 air
execute as @e[type=pig, scores={foo=1.., bar=41}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run say 41
execute as @e[type=pig, scores={foo=1.., bar=41}, tag=okok] at @s anchored eyes align xyz positioned ~ ~1 ~ if block ^ ^ ^1 stone run setblock ~ ~ ~41 air
execute if score @s thingy matches 0..20 run function demo:bar/tree_42/0_20
execute if score @s thingy matches 21..41 run function demo:bar/tree_42/21_41
say ok
say bye
execute if score @s thingy matches 0..20 run function demo:bar/tree_42/0_20
execute if score @s thingy matches 21..41 run function demo:bar/tree_42/21_41
execute if score @s thingy matches 0..28 run function demo:bar/tree_57/0_28
execute if score @s thingy matches 29..56 run function demo:bar/tree_57/29_56
```

`@function demo:foo`

```mcfunction
say 123
say (((1, 2), (1, 2)), ((1, 2), (1, 2)))
say wat
```

`@function demo:bar/tree_42/0_1`

```mcfunction
execute if score @s thingy matches 0 run say 0
execute if score @s thingy matches 1 run say 1
```

`@function demo:bar/tree_42/0_10`

```mcfunction
execute if score @s thingy matches ..5 run function demo:bar/tree_42/0_5
execute if score @s thingy matches 6.. run function demo:bar/tree_42/6_10
```

`@function demo:bar/tree_42/0_2`

```mcfunction
execute if score @s thingy matches ..1 run function demo:bar/tree_42/0_1
execute if score @s thingy matches 2 run say 2
```

`@function demo:bar/tree_42/0_20`

```mcfunction
execute if score @s thingy matches ..10 run function demo:bar/tree_42/0_10
execute if score @s thingy matches 11.. run function demo:bar/tree_42/11_20
```

`@function demo:bar/tree_42/0_5`

```mcfunction
execute if score @s thingy matches ..2 run function demo:bar/tree_42/0_2
execute if score @s thingy matches 3.. run function demo:bar/tree_42/3_5
```

`@function demo:bar/tree_42/11_12`

```mcfunction
execute if score @s thingy matches 11 run say 11
execute if score @s thingy matches 12 run say 12
```

`@function demo:bar/tree_42/11_13`

```mcfunction
execute if score @s thingy matches ..12 run function demo:bar/tree_42/11_12
execute if score @s thingy matches 13 run say 13
```

`@function demo:bar/tree_42/11_15`

```mcfunction
execute if score @s thingy matches ..13 run function demo:bar/tree_42/11_13
execute if score @s thingy matches 14.. run function demo:bar/tree_42/14_15
```

`@function demo:bar/tree_42/11_20`

```mcfunction
execute if score @s thingy matches ..15 run function demo:bar/tree_42/11_15
execute if score @s thingy matches 16.. run function demo:bar/tree_42/16_20
```

`@function demo:bar/tree_42/14_15`

```mcfunction
execute if score @s thingy matches 14 run say 14
execute if score @s thingy matches 15 run say 15
```

`@function demo:bar/tree_42/16_17`

```mcfunction
execute if score @s thingy matches 16 run say 16
execute if score @s thingy matches 17 run say 17
```

`@function demo:bar/tree_42/16_18`

```mcfunction
execute if score @s thingy matches ..17 run function demo:bar/tree_42/16_17
execute if score @s thingy matches 18 run say 18
```

`@function demo:bar/tree_42/16_20`

```mcfunction
execute if score @s thingy matches ..18 run function demo:bar/tree_42/16_18
execute if score @s thingy matches 19.. run function demo:bar/tree_42/19_20
```

`@function demo:bar/tree_42/19_20`

```mcfunction
execute if score @s thingy matches 19 run say 19
execute if score @s thingy matches 20 run say 20
```

`@function demo:bar/tree_42/21_22`

```mcfunction
execute if score @s thingy matches 21 run say 21
execute if score @s thingy matches 22 run say 22
```

`@function demo:bar/tree_42/21_23`

```mcfunction
execute if score @s thingy matches ..22 run function demo:bar/tree_42/21_22
execute if score @s thingy matches 23 run say 23
```

`@function demo:bar/tree_42/21_26`

```mcfunction
execute if score @s thingy matches ..23 run function demo:bar/tree_42/21_23
execute if score @s thingy matches 24.. run function demo:bar/tree_42/24_26
```

`@function demo:bar/tree_42/21_31`

```mcfunction
execute if score @s thingy matches ..26 run function demo:bar/tree_42/21_26
execute if score @s thingy matches 27.. run function demo:bar/tree_42/27_31
```

`@function demo:bar/tree_42/21_41`

```mcfunction
execute if score @s thingy matches ..31 run function demo:bar/tree_42/21_31
execute if score @s thingy matches 32.. run function demo:bar/tree_42/32_41
```

`@function demo:bar/tree_42/24_25`

```mcfunction
execute if score @s thingy matches 24 run say 24
execute if score @s thingy matches 25 run say 25
```

`@function demo:bar/tree_42/24_26`

```mcfunction
execute if score @s thingy matches ..25 run function demo:bar/tree_42/24_25
execute if score @s thingy matches 26 run say 26
```

`@function demo:bar/tree_42/27_28`

```mcfunction
execute if score @s thingy matches 27 run say 27
execute if score @s thingy matches 28 run say 28
```

`@function demo:bar/tree_42/27_29`

```mcfunction
execute if score @s thingy matches ..28 run function demo:bar/tree_42/27_28
execute if score @s thingy matches 29 run say 29
```

`@function demo:bar/tree_42/27_31`

```mcfunction
execute if score @s thingy matches ..29 run function demo:bar/tree_42/27_29
execute if score @s thingy matches 30.. run function demo:bar/tree_42/30_31
```

`@function demo:bar/tree_42/30_31`

```mcfunction
execute if score @s thingy matches 30 run say 30
execute if score @s thingy matches 31 run say 31
```

`@function demo:bar/tree_42/32_33`

```mcfunction
execute if score @s thingy matches 32 run say 32
execute if score @s thingy matches 33 run say 33
```

`@function demo:bar/tree_42/32_34`

```mcfunction
execute if score @s thingy matches ..33 run function demo:bar/tree_42/32_33
execute if score @s thingy matches 34 run say 34
```

`@function demo:bar/tree_42/32_36`

```mcfunction
execute if score @s thingy matches ..34 run function demo:bar/tree_42/32_34
execute if score @s thingy matches 35.. run function demo:bar/tree_42/35_36
```

`@function demo:bar/tree_42/32_41`

```mcfunction
execute if score @s thingy matches ..36 run function demo:bar/tree_42/32_36
execute if score @s thingy matches 37.. run function demo:bar/tree_42/37_41
```

`@function demo:bar/tree_42/35_36`

```mcfunction
execute if score @s thingy matches 35 run say 35
execute if score @s thingy matches 36 run say 36
```

`@function demo:bar/tree_42/37_38`

```mcfunction
execute if score @s thingy matches 37 run say 37
execute if score @s thingy matches 38 run say 38
```

`@function demo:bar/tree_42/37_39`

```mcfunction
execute if score @s thingy matches ..38 run function demo:bar/tree_42/37_38
execute if score @s thingy matches 39 run say 39
```

`@function demo:bar/tree_42/37_41`

```mcfunction
execute if score @s thingy matches ..39 run function demo:bar/tree_42/37_39
execute if score @s thingy matches 40.. run function demo:bar/tree_42/40_41
```

`@function demo:bar/tree_42/3_4`

```mcfunction
execute if score @s thingy matches 3 run say 3
execute if score @s thingy matches 4 run say 4
```

`@function demo:bar/tree_42/3_5`

```mcfunction
execute if score @s thingy matches ..4 run function demo:bar/tree_42/3_4
execute if score @s thingy matches 5 run say 5
```

`@function demo:bar/tree_42/40_41`

```mcfunction
execute if score @s thingy matches 40 run say 40
execute if score @s thingy matches 41 run say 41
```

`@function demo:bar/tree_42/6_10`

```mcfunction
execute if score @s thingy matches ..8 run function demo:bar/tree_42/6_8
execute if score @s thingy matches 9.. run function demo:bar/tree_42/9_10
```

`@function demo:bar/tree_42/6_7`

```mcfunction
execute if score @s thingy matches 6 run say 6
execute if score @s thingy matches 7 run say 7
```

`@function demo:bar/tree_42/6_8`

```mcfunction
execute if score @s thingy matches ..7 run function demo:bar/tree_42/6_7
execute if score @s thingy matches 8 run say 8
```

`@function demo:bar/tree_42/9_10`

```mcfunction
execute if score @s thingy matches 9 run say 9
execute if score @s thingy matches 10 run say 10
```

`@function demo:bar/tree_57/0_1`

```mcfunction
execute if score @s thingy matches 0 run say 0
execute if score @s thingy matches 1 run say 1
```

`@function demo:bar/tree_57/0_14`

```mcfunction
execute if score @s thingy matches ..7 run function demo:bar/tree_57/0_7
execute if score @s thingy matches 8.. run function demo:bar/tree_57/8_14
```

`@function demo:bar/tree_57/0_28`

```mcfunction
execute if score @s thingy matches ..14 run function demo:bar/tree_57/0_14
execute if score @s thingy matches 15.. run function demo:bar/tree_57/15_28
```

`@function demo:bar/tree_57/0_3`

```mcfunction
execute if score @s thingy matches ..1 run function demo:bar/tree_57/0_1
execute if score @s thingy matches 2.. run function demo:bar/tree_57/2_3
```

`@function demo:bar/tree_57/0_7`

```mcfunction
execute if score @s thingy matches ..3 run function demo:bar/tree_57/0_3
execute if score @s thingy matches 4.. run function demo:bar/tree_57/4_7
```

`@function demo:bar/tree_57/10_11`

```mcfunction
execute if score @s thingy matches 10 run say 10
execute if score @s thingy matches 11 run say 11
```

`@function demo:bar/tree_57/12_13`

```mcfunction
execute if score @s thingy matches 12 run say 12
execute if score @s thingy matches 13 run say 13
```

`@function demo:bar/tree_57/12_14`

```mcfunction
execute if score @s thingy matches ..13 run function demo:bar/tree_57/12_13
execute if score @s thingy matches 14 run say 14
```

`@function demo:bar/tree_57/15_16`

```mcfunction
execute if score @s thingy matches 15 run say 15
execute if score @s thingy matches 16 run say 16
```

`@function demo:bar/tree_57/15_18`

```mcfunction
execute if score @s thingy matches ..16 run function demo:bar/tree_57/15_16
execute if score @s thingy matches 17.. run function demo:bar/tree_57/17_18
```

`@function demo:bar/tree_57/15_21`

```mcfunction
execute if score @s thingy matches ..18 run function demo:bar/tree_57/15_18
execute if score @s thingy matches 19.. run function demo:bar/tree_57/19_21
```

`@function demo:bar/tree_57/15_28`

```mcfunction
execute if score @s thingy matches ..21 run function demo:bar/tree_57/15_21
execute if score @s thingy matches 22.. run function demo:bar/tree_57/22_28
```

`@function demo:bar/tree_57/17_18`

```mcfunction
execute if score @s thingy matches 17 run say 17
execute if score @s thingy matches 18 run say 18
```

`@function demo:bar/tree_57/19_20`

```mcfunction
execute if score @s thingy matches 19 run say 19
execute if score @s thingy matches 20 run say 20
```

`@function demo:bar/tree_57/19_21`

```mcfunction
execute if score @s thingy matches ..20 run function demo:bar/tree_57/19_20
execute if score @s thingy matches 21 run say 21
```

`@function demo:bar/tree_57/22_23`

```mcfunction
execute if score @s thingy matches 22 run say 22
execute if score @s thingy matches 23 run say 23
```

`@function demo:bar/tree_57/22_25`

```mcfunction
execute if score @s thingy matches ..23 run function demo:bar/tree_57/22_23
execute if score @s thingy matches 24.. run function demo:bar/tree_57/24_25
```

`@function demo:bar/tree_57/22_28`

```mcfunction
execute if score @s thingy matches ..25 run function demo:bar/tree_57/22_25
execute if score @s thingy matches 26.. run function demo:bar/tree_57/26_28
```

`@function demo:bar/tree_57/24_25`

```mcfunction
execute if score @s thingy matches 24 run say 24
execute if score @s thingy matches 25 run say 25
```

`@function demo:bar/tree_57/26_27`

```mcfunction
execute if score @s thingy matches 26 run say 26
execute if score @s thingy matches 27 run say 27
```

`@function demo:bar/tree_57/26_28`

```mcfunction
execute if score @s thingy matches ..27 run function demo:bar/tree_57/26_27
execute if score @s thingy matches 28 run say 28
```

`@function demo:bar/tree_57/29_30`

```mcfunction
execute if score @s thingy matches 29 run say 29
execute if score @s thingy matches 30 run say 30
```

`@function demo:bar/tree_57/29_32`

```mcfunction
execute if score @s thingy matches ..30 run function demo:bar/tree_57/29_30
execute if score @s thingy matches 31.. run function demo:bar/tree_57/31_32
```

`@function demo:bar/tree_57/29_35`

```mcfunction
execute if score @s thingy matches ..32 run function demo:bar/tree_57/29_32
execute if score @s thingy matches 33.. run function demo:bar/tree_57/33_35
```

`@function demo:bar/tree_57/29_42`

```mcfunction
execute if score @s thingy matches ..35 run function demo:bar/tree_57/29_35
execute if score @s thingy matches 36.. run function demo:bar/tree_57/36_42
```

`@function demo:bar/tree_57/29_56`

```mcfunction
execute if score @s thingy matches ..42 run function demo:bar/tree_57/29_42
execute if score @s thingy matches 43.. run function demo:bar/tree_57/43_56
```

`@function demo:bar/tree_57/2_3`

```mcfunction
execute if score @s thingy matches 2 run say 2
execute if score @s thingy matches 3 run say 3
```

`@function demo:bar/tree_57/31_32`

```mcfunction
execute if score @s thingy matches 31 run say 31
execute if score @s thingy matches 32 run say 32
```

`@function demo:bar/tree_57/33_34`

```mcfunction
execute if score @s thingy matches 33 run say 33
execute if score @s thingy matches 34 run say 34
```

`@function demo:bar/tree_57/33_35`

```mcfunction
execute if score @s thingy matches ..34 run function demo:bar/tree_57/33_34
execute if score @s thingy matches 35 run say 35
```

`@function demo:bar/tree_57/36_37`

```mcfunction
execute if score @s thingy matches 36 run say 36
execute if score @s thingy matches 37 run say 37
```

`@function demo:bar/tree_57/36_39`

```mcfunction
execute if score @s thingy matches ..37 run function demo:bar/tree_57/36_37
execute if score @s thingy matches 38.. run function demo:bar/tree_57/38_39
```

`@function demo:bar/tree_57/36_42`

```mcfunction
execute if score @s thingy matches ..39 run function demo:bar/tree_57/36_39
execute if score @s thingy matches 40.. run function demo:bar/tree_57/40_42
```

`@function demo:bar/tree_57/38_39`

```mcfunction
execute if score @s thingy matches 38 run say 38
execute if score @s thingy matches 39 run say 39
```

`@function demo:bar/tree_57/40_41`

```mcfunction
execute if score @s thingy matches 40 run say 40
execute if score @s thingy matches 41 run say 41
```

`@function demo:bar/tree_57/40_42`

```mcfunction
execute if score @s thingy matches ..41 run function demo:bar/tree_57/40_41
execute if score @s thingy matches 42 run say 42
```

`@function demo:bar/tree_57/43_44`

```mcfunction
execute if score @s thingy matches 43 run say 43
execute if score @s thingy matches 44 run say 44
```

`@function demo:bar/tree_57/43_46`

```mcfunction
execute if score @s thingy matches ..44 run function demo:bar/tree_57/43_44
execute if score @s thingy matches 45.. run function demo:bar/tree_57/45_46
```

`@function demo:bar/tree_57/43_49`

```mcfunction
execute if score @s thingy matches ..46 run function demo:bar/tree_57/43_46
execute if score @s thingy matches 47.. run function demo:bar/tree_57/47_49
```

`@function demo:bar/tree_57/43_56`

```mcfunction
execute if score @s thingy matches ..49 run function demo:bar/tree_57/43_49
execute if score @s thingy matches 50.. run function demo:bar/tree_57/50_56
```

`@function demo:bar/tree_57/45_46`

```mcfunction
execute if score @s thingy matches 45 run say 45
execute if score @s thingy matches 46 run say 46
```

`@function demo:bar/tree_57/47_48`

```mcfunction
execute if score @s thingy matches 47 run say 47
execute if score @s thingy matches 48 run say 48
```

`@function demo:bar/tree_57/47_49`

```mcfunction
execute if score @s thingy matches ..48 run function demo:bar/tree_57/47_48
execute if score @s thingy matches 49 run say 49
```

`@function demo:bar/tree_57/4_5`

```mcfunction
execute if score @s thingy matches 4 run say 4
execute if score @s thingy matches 5 run say 5
```

`@function demo:bar/tree_57/4_7`

```mcfunction
execute if score @s thingy matches ..5 run function demo:bar/tree_57/4_5
execute if score @s thingy matches 6.. run function demo:bar/tree_57/6_7
```

`@function demo:bar/tree_57/50_51`

```mcfunction
execute if score @s thingy matches 50 run say 50
execute if score @s thingy matches 51 run say 51
```

`@function demo:bar/tree_57/50_53`

```mcfunction
execute if score @s thingy matches ..51 run function demo:bar/tree_57/50_51
execute if score @s thingy matches 52.. run function demo:bar/tree_57/52_53
```

`@function demo:bar/tree_57/50_56`

```mcfunction
execute if score @s thingy matches ..53 run function demo:bar/tree_57/50_53
execute if score @s thingy matches 54.. run function demo:bar/tree_57/54_56
```

`@function demo:bar/tree_57/52_53`

```mcfunction
execute if score @s thingy matches 52 run say 52
execute if score @s thingy matches 53 run say 53
```

`@function demo:bar/tree_57/54_55`

```mcfunction
execute if score @s thingy matches 54 run say 54
execute if score @s thingy matches 55 run say 55
```

`@function demo:bar/tree_57/54_56`

```mcfunction
execute if score @s thingy matches ..55 run function demo:bar/tree_57/54_55
execute if score @s thingy matches 56 run say 56
```

`@function demo:bar/tree_57/6_7`

```mcfunction
execute if score @s thingy matches 6 run say 6
execute if score @s thingy matches 7 run say 7
```

`@function demo:bar/tree_57/8_11`

```mcfunction
execute if score @s thingy matches ..9 run function demo:bar/tree_57/8_9
execute if score @s thingy matches 10.. run function demo:bar/tree_57/10_11
```

`@function demo:bar/tree_57/8_14`

```mcfunction
execute if score @s thingy matches ..11 run function demo:bar/tree_57/8_11
execute if score @s thingy matches 12.. run function demo:bar/tree_57/12_14
```

`@function demo:bar/tree_57/8_9`

```mcfunction
execute if score @s thingy matches 8 run say 8
execute if score @s thingy matches 9 run say 9
```

`@function demo:ayy`

```mcfunction
say 123
```

`@function demo:bar/nested_execute_0`

```mcfunction
say hello
```

`@function_tag demo:ref/nothing`

```json
{
  "values": [
    "demo:ref/bar"
  ]
}
```

`@function_tag demo:nothing`

```json
{
  "values": [
    "demo:bar"
  ]
}
```

### bolt_memo

`@function bolt_memo:8qn9wmdkocxmt`

```mcfunction
say uwu
```
