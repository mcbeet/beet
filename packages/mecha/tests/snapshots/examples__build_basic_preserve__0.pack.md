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
# This is a file with comments that need to be preserved


# First command
execute as @a at @s align xyz if block ~ ~ ~ wool[foo=bar] run summon armor_stand ~ ~ ~ {Tags: ["position_history", "new"], Invisible: 1b, Marker: 1b}







        # Summon the trail











#>Some explanation
#
# Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
# tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
# quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
# consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
# cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat
# non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
tellraw @s {text: "Hover me!", hoverEvent: {action: "show_text", value: "Hi!"}}

    # The hover event is cool






say breaking news
say breaking news
say breaking news
say breaking news
say breaking news

execute as @a at @s if block ~ ~-1 ~ #wool run give @s stone{display: {Name: '[{"text": "Hello", "bold": true}]', Lore: ['[{ "text": "Something else here" }]']}}
    # When the player is on wool




    # Give a special stone block









execute if block ~ ~ ~ #namespace:tag if entity @s[tag=foo]


tellraw @a {text: "Hello # there"}



say this is a continuation


    # some comment

say wat

# Final comment
```
