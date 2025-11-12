from contextlib import contextmanager
from itertools import combinations


class Tmp:
    def __init__(self, name = None):
        if name is None:
            name = ctx.generate.format("tmp{incr}")
        self.name = name

    def __dup__(self):
        result = Tmp()
        result = self
        return result

    def __rebind__(self, rhs):
        if isinstance(rhs, Tmp):
            scoreboard players operation global self = global rhs
        else:
            scoreboard players set global self int(rhs)
        return self

    @contextmanager
    def __branch__(self):
        unless score global self matches 0:
            yield True

    def __not__(self):
        result = Tmp()
        result = 1
        unless score global self matches 0:
            result = 0
        return result

    def __eq__(self, rhs):
        result = Tmp()
        result = 0
        if isinstance(rhs, Tmp):
            if score global self = global rhs:
                result = 1
        else:
            if score global self matches int(rhs):
                result = 1
        return result

    def __str__(self):
        return self.name


for s in [7, Tmp("seven")]:
    if s == s and s == s and s == s:
        say 1

    if s == s == s == s:
        say 2


if 1 == (Tmp("foo") == Tmp("bar")) == Tmp("thing"):
    say 3


for a, b in combinations([123, 456, Tmp("foo"), Tmp("bar")], 2):
    raw #
    raw f"# check {a}, {b}"
    say (a == a == a == a)
    say (a == a == a == b)
    say (a == a == b == a)
    say (a == a == b == b)
    say (a == b == a == a)
    say (a == b == a == b)
    say (a == b == b == a)
    say (a == b == b == b)
    say (b == a == a == a)
    say (b == a == a == b)
    say (b == a == b == a)
    say (b == a == b == b)
    say (b == b == a == a)
    say (b == b == a == b)
    say (b == b == b == a)
    say (b == b == b == b)
