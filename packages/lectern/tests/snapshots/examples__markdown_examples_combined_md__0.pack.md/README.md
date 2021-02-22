# Lectern snapshot

## Data pack

### Files

- `@data_pack pack.mcmeta`

  ```json
  {
    "pack": {
      "description": "hello",
      "pack_format": 7
    }
  }
  ```

### Demo namespace

- `@function demo:foo`

  ```mcfunction
  say foo
  ```

## Resource pack

### Files

- `@resource_pack pack.mcmeta`

  ```json
  {
    "pack": {
      "pack_format": 6,
      "description": ""
    }
  }
  ```

### Minecraft namespace

- `@blockstate minecraft:grass_block`

  ```json
  {
    "variants": {
      "snowy=false": { "model": "block/grass_block" },
      "snowy=true": { "model": "block/grass_block_snow" }
    }
  }
  ```
