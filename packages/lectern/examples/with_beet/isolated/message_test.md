# Example with data pack messages

`@message isolated:my_greeting`

```json
["", { "text": "hello", "color": "red" }]
```

`@function isolated:message_demo`

```mcfunction
tellraw @a {{ "isolated:my_greeting" | msg }}
```
