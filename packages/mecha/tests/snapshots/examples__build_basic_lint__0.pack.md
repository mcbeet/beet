# Lectern snapshot

## Data pack

- `@data_pack pack.mcmeta`

  <details>

  ```json
  {
    "pack": {
      "pack_format": 7,
      "description": ""
    }
  }
  ```

  </details>

### demo

- `@function demo:foo`

  <details>

  ```mcfunction
  say hello

  # warn   Gamemode argument should go before scores. (selector_argument_order)
  # src/data/demo/functions/foo.mcfunction:3:41
  #      2 |  
  #      3 |  execute run say hello @p[scores={tmp=1},gamemode=adventure]
  #        :                                          ^^^^^^^^^^^^^^^^^^
  # warn   Redundant `execute run` clause. (execute_run)
  # src/data/demo/functions/foo.mcfunction:3:1
  #      1 |  say hello
  #      2 |  
  #      3 |  execute run say hello @p[scores={tmp=1},gamemode=adventure]
  #        :  ^^^^^^^^^^^
  execute run say hello @p[scores={tmp=1},gamemode=adventure]

  # warn   Redundant `run execute` clause. (run_execute)
  # src/data/demo/functions/foo.mcfunction:5:20
  #      4 |  
  #      5 |  execute in the_end run execute at @a run setblock ~ ~ ~ lava
  #        :                     ^^^^^^^^^^^
  execute in the_end run execute at @a run setblock ~ ~ ~ lava
  ```

  </details>
