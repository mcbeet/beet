from beet import ListOption
from dataclasses import dataclass
from pydantic.v1 import BaseModel

thing: str
thing = "hey"
say thing

num: int = 123
say num

def f(a: str, /, b: int, c: list[int] | None = None, *d: float, **kwargs: object) -> tuple[int, ...]:
    ...

say f.__annotations__

class A:
    foo: int
    bar: str = "hello"

say hasattr(A, "foo")
say A.bar
say A.__annotations__

@dataclass
class B:
    foo: list[int]
    bar: str | None = None

say B.__init__.__annotations__
say B([1, 2], "three")

class C(BaseModel):
    foo: ListOption[str] = []

for c in [C.parse_obj({"foo": "hello"}), C.parse_obj({"foo": ["hello", "world"]})]:
    say c.foo.entries()
