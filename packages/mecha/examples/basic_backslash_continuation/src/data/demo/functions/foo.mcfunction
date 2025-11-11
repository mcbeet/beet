# without multiline mode
execute \
    as @a[ \
        tag=blob \
    ] \
    run \
        function demo:foo
s\
a\
y \
h\
e\
l\
l\
o
