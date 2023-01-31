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
