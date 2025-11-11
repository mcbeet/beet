say this is a test

# Random stuff
execute
    as @a[nbt={SelectedItem: {id: "minecraft:diamond", Count: 64b}}]
    at @s  # This is important
    run setblock ~ ~ ~ repeater[delay=3, facing=south]

tellraw @a ["",
    {"text": "hello", "color": "red"},
    "not ascii: ¶",
]

say goodbye
