@data_pack pack.mcmeta
{
  "pack": {
    "min_format": [
      101,
      1
    ],
    "max_format": [
      101,
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
