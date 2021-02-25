# Lectern snapshot

## Data pack

- `@data_pack pack.mcmeta`

  <details>

  ```json
  {
    "pack": {
      "description": "hello",
      "pack_format": 7
    }
  }
  ```

  </details>

### demo

- `@function demo:foo`

  <details>

  ```mcfunction
  say foo
  ```

  </details>

## Resource pack

- `@resource_pack pack.mcmeta`

  <details>

  ```json
  {
    "pack": {
      "pack_format": 6,
      "description": ""
    }
  }
  ```

  </details>

### minecraft

- `@blockstate minecraft:grass_block`

  <details>

  ```json
  {
    "variants": {
      "snowy=false": { "model": "block/grass_block" },
      "snowy=true": { "model": "block/grass_block_snow" }
    }
  }
  ```

  </details>
