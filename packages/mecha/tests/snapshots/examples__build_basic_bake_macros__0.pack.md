# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 18,
    "description": ""
  }
}
```

### demo

`@function demo:foo`

```mcfunction
execute as @p at @s run function demo:beep/baked_6d6t4i675b87w
```

`@function demo:beep`

```mcfunction
execute positioned ~ ~1 ~ run summon creeper
$say hello $(name)
$execute as @a[name=$(name)] run say something
$execute positioned ~ ~$(offset) ~ run function demo:bop {name: "$(name)"}
```

`@function demo:bop`

```mcfunction
$say bye $(name)
```

`@function demo:beep/baked_6d6t4i675b87w`

```mcfunction
execute positioned ~ ~1 ~ run summon creeper
say hello steve
execute as @a[name=steve] run say something
execute positioned ~ ~1.3 ~ run function demo:bop/baked_6pw8q7r5nqc7y
```

`@function demo:bop/baked_6pw8q7r5nqc7y`

```mcfunction
say bye steve
```
