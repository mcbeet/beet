# Lectern snapshot

## Data pack

- `@data_pack pack.mcmeta`

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

### demo

- `@function demo:foo`

  <details>

  ```mcfunction
  @function demo:foo
  @@blah demo:foo
  @function(@@) demo:bar
  @@function(@@@) demo:bar
  @function demo:bar
  ```

  </details>
