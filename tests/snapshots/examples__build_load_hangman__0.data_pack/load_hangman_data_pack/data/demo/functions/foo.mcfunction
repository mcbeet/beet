

# This is the beginning

say hello

tellraw @s { "text": "Hover me!", "hoverEvent": { "action": "show_text", "value": "Hi!" } }

# When the player is on wool
# Give a special stone block
execute as @a at @s if block ~ ~-1 ~ #wool run give @s stone{ display: { Name: '[{ "text": "Hello", "bold": true }]', Lore: [ '[{ "text": "Something else here" }]' ] } } 1

say foo

# But what if # we # put # hash # symbols
# everywhere #
execute if block ~ ~ ~ #namespace:tag if entity @s[tag=foo]

tellraw @a { "text": "Hello # there" }

# here
tellraw @a { "text": "Hello\" # \"there" }

# thing
tellraw @s ["foo"]

# For each "player",
# start at their feet.
# Looking through their eyes,
# face perfectly at the target
# (go back to the feet)
# and move one block forward.
# Face the direction the player
# is actually facing,
# and move one block back.
# Check if we're close to the
# player's feet.
execute as @a at @s anchored eyes facing 0 0 0 anchored feet positioned ^ ^ ^1 rotated as @s positioned ^ ^ ^-1 if entity @s[distance=..0.6] run say I'm facing the target!
