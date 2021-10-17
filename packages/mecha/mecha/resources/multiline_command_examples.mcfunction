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

execute if block
    ~
        ^
            -0
        #wool

tellraw @s {
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

tellraw @a  # here
    {
        "text": "Hello\" # \"there"
    }

tellraw @s ["foo"]  # thing

say
    foo
    bar
    hello
 wat
    welp

say
    this
    is a
    # some comment
    continuation

gamerule
    doDaylightCycle
 false

gamerule
            doMobLoot
            false
                gamerule
                        doDaylightCycle
                    false
    execute as foo run
        gamemode
            survival

            @s[tag=bar]

            say hello
        execute in
            the_end
            run
            say foo
    gamerule doDaylightCycle
                         false

scoreboard players set #index global 3
scoreboard players set $index global 3
scoreboard players operation #sie_1_flags_delta integer = #sie_1_flags integer
