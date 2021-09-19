execute
    as @a
    at @s
    align xyz
    if block ~ ~ ~ #wool[
        foo = bar
    ]
    run
        summon armor_stand ~ ~ ~ {
            Tags: [
                "position_history",
                "new"
            ],
            Invisible: 1b,
            Marker: 1b
        }

execute if block 0 0 0
    #wool #this is a comment
execute if block 0 0 0 #wool #this is a comment
execute if block 0 0 0
    wool #this is a comment
execute if block 0 0 0 wool #this is a comment
