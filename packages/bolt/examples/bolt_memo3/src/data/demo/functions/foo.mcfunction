n = 5
execute function ~/{n}:
    say 1
    memo n:
        say 2
        append function ~/:
            say 3
