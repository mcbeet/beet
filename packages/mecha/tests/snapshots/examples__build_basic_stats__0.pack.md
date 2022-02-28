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

`@function demo:foo`

```mcfunction
# Analyzed 1 function
# -------------------------------------------------------------------------------
# Total commands (1 behind execute)                                      |      4
# -------------------------------------------------------------------------------
#        /scoreboard                                                     |      3
#                    objectives add <objective> <criteria>               |      1
#                    players set <targets> <objective> <score>           |      1
#                    players operation <targets> <targetObjective> <o... |      1
#        /setblock (1 behind execute)                                    |      1
#        /execute                                                        |      1
#                 if score <target> <targetObjective> matches <range>... |      1
#                 as <targets> <subcommand>                              |      1
#                 run <subcommand>                                       |      1
# -------------------------------------------------------------------------------
# Total selectors                                                        |      3
# -------------------------------------------------------------------------------
#        @e                                                              |      2
#           [tag]                                                        |      2
#           [scores]                                                     |      1
#        @s                                                              |      1
#        @e with missing or inverted type                                |      2
# -------------------------------------------------------------------------------
# Scoreboard objectives                                                  |      2
# -------------------------------------------------------------------------------
#        my_consts (dummy)                                               |      3
#                  10                                                    |      2
#        foo                                                             |      3
scoreboard objectives add my_consts dummy
scoreboard players set 10 my_consts 10
scoreboard players operation @e[tag=hello, scores={foo=1..}] foo += 10 my_consts
execute if score @s foo matches 20.. as @e[tag=hello] run setblock ~ ~ ~ stone
```
