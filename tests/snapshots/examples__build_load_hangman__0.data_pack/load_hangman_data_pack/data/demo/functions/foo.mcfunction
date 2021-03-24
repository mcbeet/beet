

# This is the beginning

say hello

tellraw @s { "text": "Hover me!", "hoverEvent": { "action": "show_text", "value": "Hi!" } }

# When the player is on wool
# Give a special stone block
execute as @a at @s if block ~ ~-1 ~ #wool run give @s stone{ display: { Name: '[{ "text": "Hello", "bold": true }]', Lore: [ '[{ "text": "Something else here" }]' ] } } 1

say foo
