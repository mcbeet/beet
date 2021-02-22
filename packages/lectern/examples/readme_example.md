# Beginner tutorial

Let's start by creating a simple function:

`@function tutorial:greeting`

```mcfunction
say Hello, world!
```

And now we can make it run when the data pack is loaded!

`@function_tag minecraft:load`

```json
{
  "values": ["tutorial:greeting"]
}
```
