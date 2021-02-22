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

### Minecraft namespace

- `@function_tag minecraft:load`

  ```json
  {
    "values": ["tutorial:greeting"]
  }
  ```
