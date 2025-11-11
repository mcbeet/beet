as @a at @s align xyz
    run summon armor_stand ~ ~ ~ {
        Tags: [
            "position_history",
            "new"
        ],
        Invisible: 1b,
        Marker: 1b
    }

if score @s obj matches 2
  say hi
