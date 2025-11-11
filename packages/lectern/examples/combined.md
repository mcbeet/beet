# Combined document

This contains both a data pack and a resource pack.

## Resource pack

Here we disable the grass block rotation randomization by creating a custom blockstate:

`@blockstate minecraft:grass_block`

```json
{
  "variants": {
    "snowy=false": { "model": "block/grass_block" },
    "snowy=true": { "model": "block/grass_block_snow" }
  }
}
```

Note that for the `snowy=false` variant we removed the rotated alternatives from the original file:

```json
{
  "variants": {
    "snowy=false": [
      { "model": "block/grass_block" },
      { "model": "block/grass_block", "y": 90 },
      { "model": "block/grass_block", "y": 180 },
      { "model": "block/grass_block", "y": 270 }
    ],
    "snowy=true": { "model": "block/grass_block_snow" }
  }
}
```

> Refer to the [Minecraft wiki](https://minecraft.gamepedia.com/Model#Example:_Grass_Block) for more details.

## Data pack

The `@data_pack` directives allows us to modify the `pack.mcmeta` file:

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "description": "hello",
    "pack_format": 7
  }
}
```

Next we're going to define a function:

`@function demo:foo`

```mcfunction
say foo
```
