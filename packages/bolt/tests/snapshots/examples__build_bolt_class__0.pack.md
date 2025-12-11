# Lectern snapshot

## Data pack

`@data_pack pack.mcmeta`

```json
{
  "pack": {
    "min_format": [
      94,
      1
    ],
    "max_format": [
      94,
      1
    ],
    "description": ""
  }
}
```

### demo

`@function demo:foo`

```mcfunction
say hello steve
say hello alex
say [<class 'demo:foo.C'>, <class 'demo:foo.A'>, <class 'demo:foo.B'>, <class 'object'>]
say ['HELLO', 'WORLD']
say hello
say bar
say value
say 42
say b
say a
say a
say b
say PreviouslyNotPossible(text='no', data='conflict')
setblock 0 0 0 air
```

`@function demo:pydantic`

```mcfunction
say {"a":123,"b":"123"}
```
