

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

execute
    if block ~ ~ ~ #namespace:tag  # But what if # we # put # hash # symbols
    if entity @s[tag=foo] # everywhere #

tellraw @a
    {
        "text": "Hello # there"
    }

tellraw @a  # here
    {
        "text": "Hello\" # \"there"
    }

tellraw @s ["foo"]  # thing

execute
  as @a                        # For each "player",
  at @s                        # start at their feet.
  anchored eyes                # Looking through their eyes,
  facing 0 0 0                 # face perfectly at the target
  anchored feet                # (go back to the feet)
  positioned ^ ^ ^1            # and move one block forward.
  rotated as @s                # Face the direction the player
                               # is actually facing,
  positioned ^ ^ ^-1           # and move one block back.
  if entity @s[distance=..0.6] # Check if we're close to the
                               # player's feet.
  run
    say I'm facing the target!
