function demo:thing1:
    say hello
    say world

    function demo:thing2:
        say this is a test

    function
        demo:thing3:
            say this
                is
                a
                test

execute as @a at @s run function demo:thing4:
    setblock ~ ~ ~ stone_pressure_plate
    setblock ~ ~-1 ~ tnt
    setblock ~ ~-2 ~ stone


execute as @a at @s run
    function demo:thing5:
        setblock ~ ~ ~ stone_pressure_plate
        setblock ~ ~-1 ~ tnt
        setblock ~ ~-2 ~ stone

execute as @a at @s:
    setblock ~ ~ ~ stone_pressure_plate

    # Some comment
    setblock ~ ~-1 ~ tnt
    setblock ~ ~-2 ~ stone

execute:
    execute as @a:
        execute at @s:
            setblock ~ ~ ~ stone_pressure_plate
            setblock ~ ~-1 ~ tnt
            setblock ~ ~-2 ~ stone

execute as @a at @s expand:
    say hello
    say world

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
    if entity @s[distance=..0.6]:   # Check if we're close to the player's feet.
        say foo
        say bar

say foo
    bar
execute
    as @a
    run say hello

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
    expand:
        say oh wow
        say this is duplicated
