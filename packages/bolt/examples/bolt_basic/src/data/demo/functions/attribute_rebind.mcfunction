from dataclasses import dataclass

@dataclass
class Var:
    name: str

    def __add__(self, value):
        result = Var(f"{self}_plus_{value}")
        say f"{result} = {self} + {value}"
        return result

    def __rebind__(self, value):
        say f"{self.name} = {value}"
        return self

    def __str__(self):
        return self.name

foo = Var("foo")
bar = Var("bar")
say f"{foo} {bar}"

foo = 123
foo += 456
foo = bar + 789
foo += bar + 999

del foo
del bar

foo = 123
bar = 456
say f"{foo} {bar}"

@dataclass
class A:
    foo: Var
    bar: Var

a = A(Var("foo"), Var("bar"))
say a

a.foo = 123
a.foo += 456
a.foo = a.bar + 789
a.foo += a.bar + 999

del a.foo
del a.bar

a.foo = 123
a.bar = 456
say a

b = {ayy: Var("ayy"), yoo: Var("yoo")}
say b

b.ayy = 123
b.ayy += 456
b.ayy = b.yoo + 789
b.ayy += b.yoo + 999

del b.ayy
del b.yoo

b["ayy"] = 123
b["yoo"] = 456
say b

c = {ayy: Var("ayy"), yoo: Var("yoo")}
say c

c["ayy"] = 123
c["ayy"] += 456
c["ayy"] = c["yoo"] + 789
c["ayy"] += c["yoo"] + 999

del c.ayy
del c.yoo

c["ayy"] = 123
c["yoo"] = 456
say c
