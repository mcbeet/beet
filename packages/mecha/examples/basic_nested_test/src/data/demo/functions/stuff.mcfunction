setblock ~ ~ ~ stone

test ~/blah:
    if block ~ ~ ~ stone say success

if block ~ ~ ~ stone function ~/remove:
    setblock ~ ~ ~ air

    test:
        say 1

    test:
        say 2
