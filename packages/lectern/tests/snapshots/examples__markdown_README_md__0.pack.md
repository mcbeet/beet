# Lectern snapshot

## Data pack

- `@data_pack pack.mcmeta`

  <details>

  ```json
  {
    "pack": {
      "pack_format": 6,
      "description": ""
    }
  }
  ```

  </details>

### tutorial

- `@function tutorial:greeting`

  <details>

  ```mcfunction
  say Hello, world!
  ```

  </details>

- `@function tutorial:obtained_dead_bush`

  <details>

  ```mcfunction
  say You obtained a dead bush!
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

### minecraft

- `@function_tag minecraft:load`

  <details>

  ```json
  {
    "values": ["tutorial:greeting"]
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
