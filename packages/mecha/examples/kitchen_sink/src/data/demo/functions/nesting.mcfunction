as @a at @s
    say hello
    say world

as @a at @s
    if score @s tmp matches 1
        say hello
        say world

function ./nesting/foo
    say
        this
        is
        a
        test


if data storage imp:temp iter.words.remaining[] function ./nesting/loop
    say wow
    if data storage imp:temp iter.words.remaining[] function ./nesting/loop
