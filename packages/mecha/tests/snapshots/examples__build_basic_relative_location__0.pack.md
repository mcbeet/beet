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

- `@function demo:bar`

  <details>

  ```mcfunction
  say hello
  ```

  </details>

- `@function demo:folder/wat`

  <details>

  ```mcfunction
  function demo:bar
  ```

  </details>

- `@function demo:foo`

  <details>

  ```mcfunction
  function demo:folder/wat
  function demo:bar
  ```

  </details>
