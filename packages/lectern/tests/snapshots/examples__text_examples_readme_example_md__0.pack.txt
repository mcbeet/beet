@data_pack pack.mcmeta
{
  "pack": {
    "min_format": [
      107,
      1
    ],
    "max_format": [
      107,
      1
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
