execute
    as @a                           # For each "player",
    at @s                           # start at their feet.
    anchored eyes                   # Looking through their eyes,
    facing 0 0 0                    # face perfectly at the target
    anchored feet                   # (go back to the feet)
    positioned ^ ^ ^1               # and move one block forward.
    rotated as @s                   # Face the direction the player
                                    # is actually facing,
    positioned ^ ^ ^-1              # and move one block back.
    if entity @s[distance=..0.6]    # Check if we're close to the
                                    # player's feet.
    run
        say I'm facing the target!
