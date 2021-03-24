

# This is the beginning

say hello

tellraw @s
    {
        "text": "Hover me!",
        "hoverEvent": {
            "action": "show_text",
            "value": "Hi!"
        }
    }

execute
    # When the player is on wool
    as @a
    at @s
    if block ~ ~-1 ~ #wool

    # Give a special stone block
    run give @s
        stone{
            display: {
                Name: '[{
                    "text": "Hello",
                    "bold": true
                }]',
                Lore: [
                    '[{ "text": "Something else here" }]'
                ]
            }
        }
        1

say foo
