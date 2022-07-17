# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 10,
    "description": ""
  }
}
```

### demo

`@function demo:foo`

```mcfunction
say 10
say 10
say 10
execute as @a run say 10
execute as @a run say 10
execute as @a run say 10
say 10
say 9
say 8
say 7
say 6
say 5
function bolt_proc_macro:generated_0
```

`@function(strip_final_newline) demo:util`

```mcfunction

```

### bolt_proc_macro

`@function bolt_proc_macro:generated_0`

```mcfunction
scoreboard players add @r counter 1
execute unless entity @a[scores={counter=10}] run function bolt_proc_macro:generated_0
```
