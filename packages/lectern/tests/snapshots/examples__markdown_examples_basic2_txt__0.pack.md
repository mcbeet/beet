# Lectern snapshot

## Data pack

- `@data_pack pack.mcmeta`

  <details>

  ```json
  {
    "pack": {
      "pack_format": 9,
      "description": ""
    }
  }
  ```

  </details>

### demo

- `@function demo:foo`

  <details>

  ```mcfunction
  say foo
  @functionn demo:foo
  say still in the same function
  @@@@
  @ @ @
  ```

  </details>

- `@function demo:bar`

  <details>

  ```mcfunction
  say bar
   @function demo:bar
   say hello
    @function demo:bar
    say world
  ```

  </details>
