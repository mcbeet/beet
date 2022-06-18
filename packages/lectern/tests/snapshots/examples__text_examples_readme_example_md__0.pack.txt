@data_pack pack.mcmeta
{
  "pack": {
    "pack_format": 10,
    "description": ""
  }
}

@function tutorial:greeting
say Hello, world!

@function_tag minecraft:load
{
  "values": ["tutorial:greeting"]
}
