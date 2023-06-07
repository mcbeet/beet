# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "pack_format": 12,
    "description": ""
  }
}
```

### demo

`@function demo:oby/nested_execute_0`

```mcfunction
execute if data storage firework:temp data.item.tag.aftermath.stats.damage run say damage, present
execute if data storage firework:temp data.item.tag.aftermath.stats.attack_speed run say attack_speed, present
execute if data storage firework:temp data.item.tag.aftermath.stats.multishot run say multishot, present
execute if data storage firework:temp data.item.tag.aftermath.stats.piercing run say piercing, present
```

`@function demo:foo`

```mcfunction
say 5
```

`@function demo:oby`

```mcfunction
execute if data storage firework:temp data.item.tag.aftermath.stats run function demo:oby/nested_execute_0
execute unless data storage firework:temp data.item.tag.aftermath.stats run say 'hi'
```
