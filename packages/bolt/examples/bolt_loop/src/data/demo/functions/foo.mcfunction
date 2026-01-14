from contextlib import contextmanager


class LoopAgainAtRuntime:
    def __init__(self, name: str):
        self.name = name

    def __bool__(self):
        function self.name
        return False


class Tmp:
    def __init__(self, name: str = None):
        if name is None:
            name = ctx.generate.format("tmp{incr}")
        self.name = name

    def __dup__(self):
        result = Tmp()
        result = self
        return result

    def __rebind__(self, rhs: object):
        if self is rhs:
            return self
        if isinstance(rhs, Tmp):
            scoreboard players operation self.name global = rhs.name global
        else:
            scoreboard players set self.name global int(rhs)
        return self

    @contextmanager
    def __branch__(self):
        unless score self.name global matches 0:
            yield True

    @contextmanager
    def __loop__(self):
        name = ctx.generate.format(~/ + "/loop{incr}")
        execute function name:
            yield LoopAgainAtRuntime(name)

    def __not__(self):
        result = Tmp()
        result = 1
        unless score self.name global matches 0:
            result = 0
        return result

    def __eq__(self, rhs: object):
        result = Tmp()
        result = 0
        if isinstance(rhs, Tmp):
            if score self.name global = rhs.name global:
                result = 1
        else:
            if score self.name global matches int(rhs):
                result = 1
        return result

    def __iadd__(self, rhs: object):
        if isinstance(rhs, Tmp):
            scoreboard players operation self.name global += rhs.name global
        else:
            scoreboard players add self.name global int(rhs)
        return self

    def __str__(self):
        return self.name


def display(value: object):
    if isinstance(value, Tmp):
        tellraw @a {"score": {"name": value.name, "objective": "global"}}
    else:
        tellraw @a {"text": f"{value}"}


def f(i):
    while not i == 4:
        display(i)
        i += 1

a = 0
f(a)

b = Tmp("b")
b = 0
f(b)
