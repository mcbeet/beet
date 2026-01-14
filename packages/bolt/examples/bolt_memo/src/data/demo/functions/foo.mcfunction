memo:
    pass

bop = 123
memo bop, foo=bop, foo:
    thing = foo
    function ./ayy:
        say thing
    say foo

a = (1, 2)
a = (a, a)
a = (a, a)

memo a, a:
    say a

say wat

a = 1
b = 2
memo a, b:
    say (a + b)
    memo b:
        say b
