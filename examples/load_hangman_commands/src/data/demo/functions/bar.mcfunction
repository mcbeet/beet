# This will be left as-is
execute as @p run say run commands

# This one works
execute as @a run commands
    # Not this one
    execute
        as @p run say
        run commands
        thing

    # But this one yes
    execute
        run
        commands
            say hello
