# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "min_format": [
      121,
      0
    ],
    "max_format": [
      121,
      0
    ],
    "description": ""
  },
  "overlays": {
    "entries": [
      {
        "directory": "dummy_overlay",
        "min_format": [
          88,
          0
        ],
        "max_format": [
          88,
          0
        ]
      }
    ]
  }
}
```

`@data_pack pack.png`

![data_pack.png](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAACXBIWXMAAAsTAAALEwEAmpwYAAACzklEQVR4nOWW6U4iQRRGv/d/AxcEAQ3BYNwiLhGjUeJKFEVw4Vlq8t3YRlmcZAx9MjM/Tlhud9e5SxVoOBym/xnRAjSiBWhEC9CIFqARLUAjWoBGtACNaAEa0QI0ogVoRAvQiBagES1AI1qARrQAjWgBGtECNKIFaEQL0IgWoBEtQCNagEa0AI1oARrRAjSiBf7qAnQ6nXR6epqen5/HYvf39xF7eXn5seTb21tqt9vBpPjl5eXU2MwK0Ol00vz8fGo2m2OxwWCQlpeX09zcXHp6evpxAQ4ODmItJzoau7m5idjKykp+BRgMBqlUKqW1tbXozmi80WikarU6tQCPj4+p3+9/fO52u1Mn5fr6OhJstVpjMT+7WCzGWrkWoNFopHK5HOKjBbCopSw+rQB7e3sh7SLc3d2lpaWldH5+Pnad437WxsbGl4IZr1uv18Pl6OgovwK02+1IzF3xq+Wz0by9vY3vr66u4gyYVgDLb21tRRF8/6Tumu3t7S9rra6upl6vF7HDw8OYQk9jrgWo1+vRfY+xF/c2cBLZvnd3fd13BTDuvBNzEqPdNd4Sjrv7fu9p8zqbm5sf+96F9rW5FqBcLn8kac7OziLRk5OTeJ2Ekx1NPuu8u5xth8/XPDw8xL3eStl3LoanYGdnZ+I6LubMC7C+vp5qtVp6fX2NUbaUF/Z7J5aRbRV3afSc8PhnY++Yi3B8fDy2TQqFQtrf3/9y8Ppe/+x+Xmt3dzdVKpUo2swL0O12Y9TdQWPJbBQ/87sz4LvPGT4YFxYWIvHFxcWYlEnPy3ULDN/3p5O+uLiIzky7xuPrSfmTNTKcsKfpu2f5PPL/ktwKMPyHEC1AI1qARrQAjWgBGtECNKIFaEQL0IgWoBEtQCNagEa0AI1oARrRAjSiBWhEC9CIFqARLUAjWoBGtACNaAEa0QI0ogVoRAvQiBagES1AI1qA5heBXAq6xs8YZAAAAABJRU5ErkJggg==)

### tutorial

`@function tutorial:greeting`

```mcfunction
say This is added before.
say Hello, world!
say This is added afterwards.
```

`@function tutorial:obtained_dead_bush`

```mcfunction
say You obtained a dead bush!
```

`@function tutorial:hidden`

```mcfunction
say This will not appear in the rendered markdown.
```

`@function tutorial:also_hidden`

```mcfunction
say This is also hidden.
```

`@function(strip_final_newline) tutorial:stripped`

```mcfunction
say This function doesn't have a final newline.
```

`@advancement tutorial:obtained_dead_bush`

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

`@function_tag(strip_final_newline) tutorial:something_else`

```json
{
  "values": ["tutorial:stripped"]
}
```

`@function_tag tutorial:from_github`

```json
say foo
```

### minecraft

`@function_tag minecraft:load`

```json
{
  "values": [
    "tutorial:greeting",
    "#tutorial:something_else"
  ]
}
```

`@loot_table minecraft:blocks/diamond_ore`

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

`@loot_table minecraft:blocks/yellow_shulker_box`

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

### text_in_block

`@function text_in_block:foo`

```mcfunction
say foo
```

## Overlay `dummy_overlay`

`@overlay dummy_overlay`

### tutorial

`@function tutorial:greeting`

```mcfunction
say Hello from overlay!
```

`@endoverlay`
