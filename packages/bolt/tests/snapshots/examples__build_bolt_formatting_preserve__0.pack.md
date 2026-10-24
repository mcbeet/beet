# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "min_format": [
      121,
      0
    ],
    "max_format": [
      121,
      0
    ],
    "description": ""
  }
}
```

### demo

`@function demo:foo`

```mcfunction
# top level comment
say example

    #inner comment


# comment before the loop


execute if score #test test matches 0 run function demo:foo/test
execute if score #test test matches 0 run function demo:foo/test
execute if score #test test matches 1 run function demo:foo/test
execute if score #test test matches -1 run function demo:foo/test
execute if score #test test matches 2 run function demo:foo/test
execute if score #test test matches -2 run function demo:foo/test
execute if score #test test matches 3 run function demo:foo/test
execute if score #test test matches -3 run function demo:foo/test
execute if score #test test matches 4 run function demo:foo/test
execute if score #test test matches -4 run function demo:foo/test
say command
# comment after the loop
```

`@function demo:foo/test`

```mcfunction
# top level comment


    #inner comment
say test

# comment before the loop





# comment after the loop
```
