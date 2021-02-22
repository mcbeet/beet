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

### Demo namespace

- `@function demo:foo`

  ```mcfunction
  say foo
  @functionn demo:foo
  say still in the same function
  @@@@
  @ @ @
  ```

- `@function demo:bar`

  ```mcfunction
  say bar
   @function demo:bar
   say hello
    @function demo:bar
    say world
  ```
