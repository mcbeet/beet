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
<class 'mecha.ast.AstRoot'>
  commands:
    <class 'mecha.ast.AstCommand'>
      identifier: 'say:message'
      arguments:
        <class 'mecha.ast.AstMessage'>
          fragments:
            <class 'mecha.ast.AstMessageText'>
              value: 'hello'
```

`@function demo:bar`

```mcfunction
<class 'mecha.ast.AstRoot'>
  location: SourceLocation(pos=0, lineno=1, colno=1)
  end_location: SourceLocation(pos=10, lineno=2, colno=1)
  commands:
    <class 'mecha.ast.AstCommand'>
      location: SourceLocation(pos=0, lineno=1, colno=1)
      end_location: SourceLocation(pos=9, lineno=1, colno=10)
      identifier: 'say:message'
      arguments:
        <class 'mecha.ast.AstMessage'>
          location: SourceLocation(pos=4, lineno=1, colno=5)
          end_location: SourceLocation(pos=9, lineno=1, colno=10)
          fragments:
            <class 'mecha.ast.AstMessageText'>
              location: SourceLocation(pos=4, lineno=1, colno=5)
              end_location: SourceLocation(pos=9, lineno=1, colno=10)
              value: 'hello'
```
