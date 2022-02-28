# Lectern snapshot

## Data pack

- `@data_pack pack.mcmeta`

  <details>

  ```json
  {
    "pack": {
      "pack_format": 9,
      "description": ""
    }
  }
  ```

  </details>

- `@data_pack pack.png`

  <details>

  ![data_pack.png](pack.png)

  </details>

### tutorial

- `@function tutorial:greeting`

  <details>

  ```mcfunction
  say This is added before.
  say Hello, world!
  say This is added afterwards.
  ```

  </details>

- `@function tutorial:obtained_dead_bush`

  <details>

  ```mcfunction
  say You obtained a dead bush!
  ```

  </details>

- `@function tutorial:hidden`

  <details>

  ```mcfunction
  say This will not appear in the rendered markdown.
  ```

  </details>

- `@function tutorial:also_hidden`

  <details>

  ```mcfunction
  say This is also hidden.
  ```

  </details>

- `@function(strip_final_newline) tutorial:stripped`

  <details>

  ```mcfunction
  say This function doesn't have a final newline.
  ```

  </details>

- `@advancement tutorial:obtained_dead_bush`

  <details>

  ```json
  {
    "criteria": {
      "dead_bush": {
        "trigger": "minecraft:inventory_changed",
        "conditions": {
          "items": [
            {
              "item": "minecraft:dead_bush"
            }
          ]
        }
      }
    },
    "requirements": [
      [
        "dead_bush"
      ]
    ],
    "rewards": {
      "function": "tutorial:obtained_dead_bush"
    }
  }
  ```

  </details>

- `@function_tag(strip_final_newline) tutorial:something_else`

  <details>

  ```json
  {
    "values": ["tutorial:stripped"]
  }
  ```

  </details>

- `@function_tag tutorial:from_github`

  <details>

  ```json
  say foo
  ```

  </details>

### minecraft

- `@function_tag minecraft:load`

  <details>

  ```json
  {
    "values": [
      "tutorial:greeting",
      "#tutorial:something_else"
    ]
  }
  ```

  </details>

- `@loot_table minecraft:blocks/diamond_ore`

  <details>

  ```json
  {
    "pools": [
      {
        "rolls": 1,
        "entries": [
          {
            "type": "minecraft:item",
            "name": "minecraft:dead_bush"
          }
        ]
      }
    ]
  }
  ```

  </details>

- `@loot_table minecraft:blocks/yellow_shulker_box`

  <details>

  ```json
  {
    "type": "minecraft:block",
    "pools": [
      {
        "rolls": 1,
        "entries": [
          {
            "type": "minecraft:alternatives",
            "children": [
              {
                "type": "minecraft:dynamic",
                "name": "minecraft:contents",
                "conditions": [
                  {
                    "condition": "minecraft:match_tool",
                    "predicate": {
                      "item": "minecraft:air",
                      "nbt": "{drop_contents:1b}"
                    }
                  }
                ]
              },
              {
                "type": "minecraft:item",
                "name": "minecraft:yellow_shulker_box",
                "functions": [
                  {
                    "function": "minecraft:copy_name",
                    "source": "block_entity"
                  },
                  {
                    "function": "minecraft:copy_nbt",
                    "source": "block_entity",
                    "ops": [
                      {
                        "source": "Lock",
                        "target": "BlockEntityTag.Lock",
                        "op": "replace"
                      },
                      {
                        "source": "LootTable",
                        "target": "BlockEntityTag.LootTable",
                        "op": "replace"
                      },
                      {
                        "source": "LootTableSeed",
                        "target": "BlockEntityTag.LootTableSeed",
                        "op": "replace"
                      }
                    ]
                  },
                  {
                    "function": "minecraft:set_contents",
                    "entries": [
                      {
                        "type": "minecraft:dynamic",
                        "name": "minecraft:contents"
                      }
                    ]
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  }
  ```

  </details>
