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
