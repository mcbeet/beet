# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 41,
    "description": ""
  }
}
```

### demo

`@function demo:minify`

```mcfunction
say this is a test
execute as @a[nbt={SelectedItem:{id:"minecraft:diamond",Count:64b}}] at @s run setblock ~ ~ ~ repeater[delay=3,facing=south]
tellraw @a ["",{"text":"hello","color":"red"},"not ascii: \u00b6"]
say goodbye
```

`@function demo:dense`

```mcfunction
say this is a test
execute as @a[nbt={SelectedItem: {id: "minecraft:diamond", Count: 64b}}] at @s run setblock ~ ~ ~ repeater[delay=3, facing=south]
tellraw @a ["", {"text": "hello", "color": "red"}, "not ascii: \u00b6"]
say goodbye
```

`@function demo:preserve`

```mcfunction
say this is a test

# Random stuff
execute as @a[nbt={SelectedItem: {id: "minecraft:diamond", Count: 64b}}] at @s run setblock ~ ~ ~ repeater[delay=3, facing=south]




tellraw @a ["", {"text": "hello", "color": "red"}, "not ascii: \u00b6"]




say goodbye
```

`@function demo:funky`

```mcfunction
say this is a test

# Random stuff
execute as @a[nbt={SelectedItem:{id:"minecraft:diamond",Count:64b}}] at @s run setblock ~ ~ ~ repeater[delay=3, facing=south]




tellraw @a ["", {"color": "red", "text": "hello"}, "not ascii: ¶"]




say goodbye
```
