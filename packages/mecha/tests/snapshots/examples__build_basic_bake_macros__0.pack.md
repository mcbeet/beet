# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 14,
    "description": ""
  }
}
```

### demo

`@function demo:foo`

```mcfunction
execute as @p at @s run function demo:beep/baked_6pw8q7r5nqc7y
```

`@function demo:beep`

```mcfunction
$say hello $(name)
$execute positioned ~ ~1 ~ run function demo:bop {name: "$(name)"}
```

`@function demo:bop`

```mcfunction
$say bye $(name)
```

`@function demo:beep/baked_6pw8q7r5nqc7y`

```mcfunction
say hello steve
execute positioned ~ ~1 ~ run function demo:bop/baked_6pw8q7r5nqc7y
```

`@function demo:bop/baked_6pw8q7r5nqc7y`

```mcfunction
say bye steve
```

## Resource pack

`@resource_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 14,
    "description": ""
  }
}
```
