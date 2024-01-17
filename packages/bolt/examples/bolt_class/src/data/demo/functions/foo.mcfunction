from dataclasses import dataclass

class Foo:
    def __init__(self, name):
        self.name = name

say f"hello {Foo("steve").name}"

class Bar(Foo):
    def __init__(self):
        super().__init__("alex")

say f"hello {Bar().name}"

class A:
    pass
class B:
    pass
class C(A, B):
    pass

say C.mro()

things = []

@things.append
@str.upper
@str
@object.__new__
class Thing1:
    def __str__(self):
        return "hello"

@things.append
@str.upper
@str
@object.__new__
class Thing2:
    def __str__(self):
        return "world"

say things

class Weird:
    say hello

class Ayy:
    def bar(self):
        say bar

Ayy().bar()

class GG:
    def __init__(self):
        Hmm().damn()

class Hmm:
    value = 42

    def damn(self):
        say value
        say self.value

GG()

class A:
    def b(self):
        say b
        return B()

class B:
    def a(self):
        say a
        return A()

A().b().a()
B().a().b()

@dataclass
class PreviouslyNotPossible:
    text: str
    data: str

    @staticmethod
    def you_can_do_this():
        setblock = 0
        setblock setblock setblock setblock air

say PreviouslyNotPossible("no", "conflict")
PreviouslyNotPossible.you_can_do_this()
