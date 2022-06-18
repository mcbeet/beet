# Lectern snapshot

## Data pack

- `@data_pack pack.mcmeta`

  <details>

  ```json
  {
    "pack": {
      "pack_format": 10,
      "description": ""
    }
  }
  ```

  </details>

### tutorial

- `@function tutorial:greeting`

  <details>

  ```mcfunction
  say Hello, world!
  ```

  </details>

### minecraft

- `@function_tag minecraft:load`

  <details>

  ```json
  {
    "values": ["tutorial:greeting"]
  }
  ```

  </details>
