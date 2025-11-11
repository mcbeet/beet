# This is a file with comments that need to be preserved


# First command
execute
    as @a
    at @s
    align xyz
    if block ~ ~ ~ wool[
        foo = bar
    ]
    run
        # Summon the trail
        summon armor_stand ~ ~ ~ {
            Tags: [
                "position_history",
                "new"
            ],
            Invisible: 1b,
            Marker: 1b
        }



#>Some explanation
#
# Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
# tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
# quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
# consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
# cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat
# non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
tellraw @s {
    "text": "Hover me!",
    # The hover event is cool
    "hoverEvent": {
        "action": "show_text",
        "value": "Hi!"
    }
}

say breaking news
say breaking news
say breaking news
say breaking news
say breaking news

execute
    # When the player is on wool
    as @a
    at @s
    if block ~ ~-1 ~ #wool

    # Give a special stone block
    run give @s stone{
        display: {
            Name: '[{"text": "Hello", "bold": true}]',
            Lore: [
                '[{ "text": "Something else here" }]',
            ]
        }
    }

execute
    if block ~ ~ ~ #namespace:tag  # But what if # we # put # hash # symbols
    if entity @s[tag=foo] # everywhere #
tellraw @a {
    "text": "Hello # there"
}

say
    this
    is a
    # some comment
    continuation
say wat

# Final comment
