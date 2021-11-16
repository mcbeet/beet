# Lectern snapshot

## Data pack

- `@data_pack pack.mcmeta`

  <details>

  ```json
  {
    "pack": {
      "pack_format": 7,
      "description": ""
    }
  }
  ```

  </details>

### demo

- `@function demo:foo`

  <details>

  ```mcfunction
  say Hello @a[tag=!registered]
  execute if score #init temp = #wat temp run say Hello @a[tag=hi]
  ```

  </details>
