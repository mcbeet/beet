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

`@function demo:foo`

```mcfunction
say ('start', 'screen', {'w': '64', 'h': '64', 'd': '2', 'name': 'test'})
say ('start', 'group', {'key': 'buttons', 'background': 'test_background'})
say ('start', 'button', {'key': '1', 'x': '6', 'y': '6', 'default': 'ok_button', 'hover': 'arrow_down_1'})
say ('end', 'button', {'key': '1', 'x': '6', 'y': '6', 'default': 'ok_button', 'hover': 'arrow_down_1'})
say ('start', 'button', {'key': '2', 'x': '42', 'y': '6', 'default': 'ok_button', 'hover': 'ok_button_hover'})
say ('end', 'button', {'key': '2', 'x': '42', 'y': '6', 'default': 'ok_button', 'hover': 'ok_button_hover'})
say ('end', 'group', {'key': 'buttons', 'background': 'test_background'})
say ('end', 'screen', {'w': '64', 'h': '64', 'd': '2', 'name': 'test'})
```
