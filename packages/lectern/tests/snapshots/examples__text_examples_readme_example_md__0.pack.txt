@data_pack pack.mcmeta
{
  "pack": {
    "min_format": [
      88,
      0
    ],
    "max_format": [
      88,
      0
    ],
    "description": ""
  }
}

@function tutorial:greeting
say Hello, world!

@function_tag minecraft:load
{
  "values": ["tutorial:greeting"]
}
