execute run commands
	say Hello world!
	give @s minecraft:diamond 64  # One stack should be enough

execute
    # First we select all players
    as @a at @s
    if block ~ ~-1 ~ minecraft:air
    run commands  # Blah blah this is a trailing comment
        say Hello world!
        # This give command is pretty long
        give @s
            minecraft:stone{
                display: {
                    Name: '[{
                        "text": "Hello",
                        "bold": true  # Bold makes it easier to read
                    }]',
                    Lore: [
                        # Pretty sure we don't need this
                        '[{ "text": "Something else here" }]'
                    ]
                }
            }
            1

        # Now we add some space

        say Lorem ipsum dolor sit amet, consectetur adipiscing
            elit, sed do eiusmod tempor incididunt ut labore et
            dolore magna aliqua. Ut enim ad minim veniam, quis
            nostrud exercitation ullamco laboris nisi ut aliquip
            ex ea commodo consequat. Duis aute irure dolor in
            reprehenderit in voluptate velit esse cillum dolore
            eu fugiat nulla pariatur. Excepteur sint occaecat
            cupidatat non proident, sunt in culpa qui officia
            deserunt mollit anim id est laborum

execute as @e[type=minecraft:cow] at @s run commands
	data modify entity @s Motion[1] set value 5.0f
	particle minecraft:cloud ~ ~ ~ 0 0 0 0.1 10 normal

execute as @a run commands
    execute
        facing entity @e[tag=target,limit=1,sort=nearest] eyes
        run commands
            say Boom!
    say and we're done

execute run commands
    execute run commands
        execute run commands
            execute run commands
                execute run commands
                    say 1
                say 2
            say 3
        say 4
    say 5


say something



    this isn't the end
