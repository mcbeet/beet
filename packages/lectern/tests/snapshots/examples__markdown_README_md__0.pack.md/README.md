# Lectern snapshot

## Data pack

### Files

- `@data_pack pack.mcmeta`

  ```json
  {
    "pack": {
      "pack_format": 6,
      "description": ""
    }
  }
  ```

### Tutorial namespace

- `@function tutorial:greeting`

  ```mcfunction
  say Hello, world!
  ```

- `@function tutorial:obtained_dead_bush`

  ```mcfunction
  say You obtained a dead bush!
  ```

- `@advancement tutorial:obtained_dead_bush`

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

### Minecraft namespace

- `@function_tag minecraft:load`

  ```json
  {
    "values": ["tutorial:greeting"]
  }
  ```

- `@loot_table minecraft:blocks/diamond_ore`

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
