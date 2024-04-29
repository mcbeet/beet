# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 41,
    "description": ""
  }
}
```

### demo

`@function demo:foo`

```mcfunction
say this is not compiled

value = 123
print(value)

# As long as you don't mc.compile(ctx.data) or include "mecha" in the pipeline
# you can leverage mecha's compiler and the bolt runtime for other purposes
# without affecting function files in the output pack.
```

### minecraft

`@recipe minecraft:arrow`

```json
{
  "type": "minecraft:crafting_shaped",
  "category": "equipment",
  "key": {
    "#": {
      "tag": "minecraft:coals"
    },
    "Y": {
      "item": "minecraft:feather"
    }
  },
  "pattern": [
    "#",
    "#",
    "Y"
  ],
  "result": {
    "count": 9,
    "item": "minecraft:arrow"
  },
  "show_notification": true
}
```

`@recipe minecraft:spectral_arrow`

```json
{
  "type": "minecraft:crafting_shaped",
  "category": "equipment",
  "key": {
    "#": {
      "tag": "minecraft:coals"
    },
    "X": {
      "item": "minecraft:arrow"
    }
  },
  "pattern": [
    " # ",
    "#X#",
    " # "
  ],
  "result": {
    "count": 7,
    "item": "minecraft:spectral_arrow"
  },
  "show_notification": true
}
```

`@recipe minecraft:tipped_arrow`

```json
{
  "type": "minecraft:crafting_special_tippedarrow",
  "category": "misc"
}
```
