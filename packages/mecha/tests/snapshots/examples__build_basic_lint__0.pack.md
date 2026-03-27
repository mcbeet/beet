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
say hello

#>WARN   Gamemode argument should go before scores. (selector_argument_order)
# src/data/demo/functions/foo.mcfunction:3:41
#      2 |  
#      3 |  execute run say hello @p[scores={tmp=1},gamemode=adventure]
#        :                                          ^^^^^^^^^^^^^^^^^^
#>WARN   Redundant `execute run` clause. (execute_run)
# src/data/demo/functions/foo.mcfunction:3:1
#      1 |  say hello
#      2 |  
#      3 |  execute run say hello @p[scores={tmp=1},gamemode=adventure]
#        :  ^^^^^^^^^^^
execute run say hello @p[scores={tmp=1},gamemode=adventure]

#>WARN   Redundant `run execute` clause. (run_execute)
# src/data/demo/functions/foo.mcfunction:5:20
#      4 |  
#      5 |  execute in the_end run execute at @a run setblock ~ ~ ~ lava
#        :                     ^^^^^^^^^^^
execute in the_end run execute at @a run setblock ~ ~ ~ lava

#>WARN   Duplicate execute clause. (duplicate_execute)
# src/data/demo/functions/foo.mcfunction:7:15
#      6 |  
#      7 |  execute at @s at @s run say test
#        :                ^^^^^
execute at @s at @s run say test
```
