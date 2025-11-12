# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "min_format": [
      88,
      0
    ],
    "max_format": [
      88,
      0
    ],
    "description": ""
  }
}
```

### demo

`@function demo:foo`

```mcfunction
say []
execute as @s run say [('execute:subcommand', ()), ('execute:as:targets:subcommand', (AstSelector(variable='s', arguments=AstChildren(())),)), ('execute:run:subcommand', ())]
execute if score foo temp matches 77 run say [('execute:subcommand', ()), ('execute:if:score:target:targetObjective:matches:range:subcommand', (AstPlayerName(value='foo'), AstObjective(value='temp'), AstRange(min=77, max=77))), ('execute:commands', ())]
say []
```

`@function demo:thing`

```mcfunction
say [('execute:subcommand', ()), ('execute:if:score:target:targetObjective:matches:range:subcommand', (AstPlayerName(value='foo'), AstObjective(value='temp'), AstRange(min=77, max=77))), ('execute:commands', ()), ('function:name:commands', (AstResourceLocation(is_tag=False, namespace='demo', path='thing'),))]
```
