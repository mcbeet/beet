0
###
123
###
123.456
###
22220099.6667e-3
###
0.67e6
###
1 + 2
###
1 - 2
###
1 - 2 + 3
###
1 - (2 + 3)
###
2 + -54
###
2 + -54 * 10
###
(2 + -54) * 10
###
---64+++64
###
1 * 2 / 3 * 4
###
1 * 2 / (3 * 4)
###
16 // 5 % 7
###
-2 ** 3 + +4 * 5 // 6 / 7 % 9 + 10 - 11 << 12 >> 13 & 14 ^ 15 | 16
###
False or True and "hello" or not "foo" == "bar" or 1 != 2 and 1 < 2 and 2 <= 3 and 5 > 4 and 6 >= 5 and 1 in 1 and 2 not in 2 and 3 is 3 and 3 is not 3
###
64 §§§
###
17 % %3
###
True and (False or True)
###
"this"
###
"this\nthat"
###
"\"\u2588this\nthat"
###
''
###
'"\'"'
###
'something \t\f\n\\\'here'
###
'abc\"'
###
"hey" "hey"
###
None
###
foo
###
"hello" + foo
###
foo = 1
foo
###
foo = 1
"hello" + foo
###
a = 1
if a == 1:
    a = 0
###
if True:
    say hello
elif True or False:
    say hello
else:
    say hello
###
if True:
    say hello
elif True or False:
    say hello
else "blah":
    say hello
###
if True:
    say hello
a = 1
else:
    say hello
###
if
###
if True and
###
if True:
say hello
###
while True:
    say hello
###
if score @s tmp matches 0:
    if "thing" == "bar":
        say hello
    if "thing" == "foo":
        say hello
###
if score @s tmp matches 0:
    if "thing" == "foo":
        say hello
###
if score @s tmp matches 0:
    while True:
        say hello
    while True:
        say hello
###
if score @s tmp matches 0:
    while True:
        say hello
###
if score @s tmp matches 42:
    count = 42
    while count > 0:
        say hello
        count = count - 1
###
foo = (
    "abc"
    + "def"
)
###
1 * 2
* 3
###
true | false | null
###
foo = 1
foo == 1
###
for c in "abc":
    say something
###
foo = foo
###
foo = 1
foo = foo
###
for foo in foo:
    foo = foo
###
for foo in "foo":
    foo = foo
###
foo += "hey"
###
foo = ""
foo += "hey"
###
wat = the = "f"
###
break
###
continue
###
if true:
    break
###
for i in "":
    say hello
    continue
###
while false:
    break
###
for i in "abc":
    if i == "b":
        break
###
"foo".bar
###
"foo".bar.baz
###
"foo".bar()[0]
###
"foo".bar()[0]."hello".99."with space"("thing" * 7)
###
"foo"(
    1,
    2,
    3,
)
###
def foo():
    say hello
foo()
###
def foo():
    def bar():
        foo()
    bar()
###
def foo(
    a=1,
    b=a,
    c=a + b,
):
    say hello
###
def f
###
def f()
###
def f():
say yolo
###
def f(a=a):
    say wat
###
def f(a, b=a):
    b += a
    say wat
###
def f(a, b):
    def g(c):
        a + b
    c
g()
###
def f(a, b):
    def g(c):
        a + b
    f(c)
###
def foo(something):
    def wat():
        say
            yo
            wat
            is
            dat
# this is a comment
        x = "hello"
        for i in somehng:
            x += i * 3

        say wow
    wat()
###
def foo(something):
    def wat():
        say
            yo
            wat
            is
            dat
# this is a comment
        x = "hello"
        for i in something:
            x += i * 3

        say wow
    wat()
###
def foo():
    global thing
    thing += bar()
def bar():
    global thing
    thing += foo()
thing = bar()
###
def foo():
    bar() + thing
def bar():
    foo() + thin
thing = bar()
###
def foo():
    return
###
return "hello"
###
return foo
###
def f():
    def g():
        return foo
    foo = 0
###
def f():
    foo = 0
f(foo)
###
def f(x):
    tellraw @a x
f("thing")
###
def f(x):
    tellraw @a xx
f("thing")
###
{
    foo: "bar"
}
###
foo = "hello"
{
    foo: "bar"
}
###
foo = "hello"
{
    "foo": foo
}
###
foo = "hello"
{
    foo * 3: 42,
    16 + 3: [],
}
###
my_predicate = {
  "condition": "minecraft:entity_scores",
  "entity": "this",
  "scores": {
    "score1": {
      "min": {
        "type": "minecraft:score",
        "target": "this",
        "score": "score2",
        "scale": 1
      }
    }
  }
}
###
my_predicate = {
  condition: "minecraft:entity_scores",
  entity: "this",
  scores: {
    score1: {
      "min": {
        type: "minecraft:score",
        target: "this",
        score: "score2",
        scale: 1
      }
    }
  }
}
###
def f():
    return {f(): f(), "other": [{}, {}, "wat"]}
###
at @s if "foo" == "bar":
    say yolo
###
at @s for i in "foo":
    say yolo
###
say hello
###
def wat():
    say hello
###
a = ''
tellraw @p a
###
foo = '[{"text": "Hello", "bold": true}]'
as @a at @s if block ~ ~-1 ~ #wool give @s stone{
    display: {
        Name: foo,
        Lore: [
            '[{ "text": "Something else here" }]',
        ]
    }
}
###
thing = (1, 'hey') + () + ("wow",)
###
f"hello"
###
foo = "world"
f"hello {foo}"
###
foo = "world"
f"hello {foo!r}"
###
f"hello {1 + 1}"
###
f"hello {1 + 1:03}"
###
f'{{}}nope{1}'
###
yo = f"{{{f"{{{f"{{{7:08}}}"}}}"}}}"
###
yo = f""
###
yo = f"\""
###
yo = f"\\"
###
yo = f"}"
###
yo = f'thing \e'
###
x = 8
if score @s tmp matches (x, None) say wat
###
def f():
    yield 1
    yield 2
    yield 3
for i in f():
    say i
###
if True:
    yield
###
def f():
    yield
###
import demo:foo
###
import ./thing
###
import wat/is/that
###
from wat/is/that import foo
###
import math
mah.sin(1)
###
import math
math.sin(1)
###
import math as m
m.sin(1)
###
from demo:foo import thing
say thing
###
def f():
    from demo:foo import a b c
say a
###
if score @s tmp matches 1.. if entity @p[tag=foo]:
    if True:
        say 42
    else:
        say no
###
setblock = 0
###
if 1:
    say 1
elif 2:
    say 2
elif 3:
    say 3
elif 4:
    say 4
###
if 1:
    say 1
elif 2:
    say 2
elif 3:
    say 3
elif 4:
    say 4
say done
###
if 1:
    say 1
elif 2:
    say 2
elif 3:
    say 3
elif 4:
    say 4
else:
    say other
###
if 1:
    say 1
elif 2:
    say 2
elif 3:
    say 3
elif 4:
    say 4
else:
    say other
say done
###
execute
    as @a                        # For each "player",
    at @s                        # start at their feet.
    anchored eyes                # Looking through their eyes,
    facing 0 0 0                 # face perfectly at the target
    anchored feet                # (go back to the feet)
    positioned ^ ^ ^1            # and move one block forward.
    rotated as @s                # Face the direction the player
                                    # is actually facing,
    positioned ^ ^ ^-1           # and move one block back.
    if entity @s[distance=..0.6]:
        say foo
        say bar
###
say foo
    bar
execute
    as @a
    run say hello
###
while True:
    if "hello":
        pass
    else:
        break
###
for node in generate_tree("abcdefghijklmnopqrstuvwxyz0123456789"):
    append function node.parent:
        if node.partition(5):
            if score @s thingy matches node.range function node.children
        else:
            if score @s thingy matches node.range say node.value
###
print(ctx.directory, __name__)
###
a = 1
setblock a 2 3 stone
###
a = "1 2 3"
setblock a stone
###
a = 1
if block ^ f"^{a}" ^ #planks say 42
###
if block ("~", "~", "~") #planks say 42
###
a = [][]
###
def f():
    pass
f(1, 2, thing=3, 4)
###
def f():
    pass
f(1, 2, **{"thing": 3}, 4)
###
def f():
    pass
f(1, 2, thing=3, *[4])
###
def f():
    pass
f(1, 2, **{"thing": 3}, *[4])
###
def f():
    pass
f(1, 2, thing=3)
###
def f():
    pass
f(1, 2, **{"thing": 3})
###
def f():
    pass
f(1, *[4], 2, thing=3)
###
def f():
    pass
f(1, *[4], 2, **{"thing": 3})
###
[*"abc"]
###
[**"abc"]
###
{**{1: 1}}
###
{*{1: 1}}
###
foo.bar = 1
###
foo().bar = 1
###
def f():
    f.data = {}
###
d = {}
d[1] = {}
d[1][2] = "foo"
###
d = {foo: 1}
d.foo += 1
###
scoreboard objectives setdisplay list some_score_name
###
color = "red"
scoreboard objectives setdisplay f"sidebar.team.{color}" some_score_name
###
my_team = "sidebar.team.red"
scoreboard objectives setdisplay my_team some_score_name
###
item replace block ~ ~2 ~ container.26 with minecraft:spruce_sapling 4
###
weapon = "thing"
item replace entity @s weapon.offhand from entity @s weapon.mainhand
###
my_weapon = {offhand: "weapon.offhand", mainhand: "weapon.mainhand"}
item replace entity @s my_weapon.offhand from entity @s my_weapon.mainhand
###
numbers = list(range(12))
say numbers[3:]
###
numbers = list(range(12))
numbers[3:] = []
###
numbers = list(range(12))
del numbers[3:]
###
del 1 + 1
###
execute function demo:foo:
###
mykey = "aaa"
if data storage some:path/to/storage f'some.{mykey}.path{{my: "compound"}}' run say hi
###
mypath = 'some.path{my: "compound"}.stuff[42].beep[{my: "subscript"}].boop'
if data storage some:path/to/storage (mypath) run say hi
###
entity_type = "creeper"
at @e[type=entity_type] summon lightning_bolt
###
append function demo:foo
###
function_tag
###
merge function_tag
###
merge function_tag minecraft:tick
###
demo:foo
###
a = demo:foo/bar
###
for class in "abc":
    scoreboard objectives add class dummy
###
a = 1
positioned ~ ~a ~ function demo:foo
###
a, b = "ab"
###
for i, value in enumerate("abc"):
    say f"{i}: {value}"
###
global x
###
x = 1
global x
###
x = 1
def f():
    global xx
###
def f(x):
    global x
###
x = 1
def f():
    global x
    nonlocal x
###
math = 0
say math
def wat():
    global math
    import math
wat()
say math.ceil(0.1)
###
def init_global_score(self, name):
    self.name = name

def rebind_global_score(self, rhs):
    if isinstance(rhs, GlobalScore):
        scoreboard players operation self.name global = rhs.name global
    else:
        scoreboard players set self.name global rhs
    return self

GlobalScore = type("GlobalScore", (), {"__init__": init_global_score, "__rebind__": rebind_global_score})

a = GlobalScore("a")
a = 123
a = 456

b = GlobalScore("b")
b = 789
b = a
###
def Counter(x=0):
    def incr():
        nonlocal x
        x += 1
        return x
    return {"incr": incr}

counter = Counter()
say counter.incr()
say counter.incr()
say Counter(9).incr()
###
for i in range(3):
    parent[i] = f"param{i}"
###
def foo(value):
    if value:
        result = 1
    else:
        result = 0
    return result
###
def foo(value):
    result = "init"
    if value:
        result = 1
    else:
        result = 0
    return result
###
tag_name = foo:bar
function #tag_name
###
for a in [False, True]:
    for b in [False, True]:
        for c in [False, True]:
            for d in [False, True]:
                print((a and b or c and not d) in [True] not in [False])
###
a = 1
def f():
    a += 1
###
a = 2
say a
###
a = 2
say a normal message
###
a = 2
say a
    normal
    message
###
"hey"
    "hey"
###
bow_data = {CustomModelData: 7}
give @s bow{**bow_data}
###
custom_model_data = {CustomModelData: 7}
stone_can_place_on = ["minecraft:dirt"]
give @s stone{CanPlaceOn: [*stone_can_place_on], **custom_model_data}
###
red = {"color": "red"}
tellraw @p ["", {"text": "hey", **red}, *red.color]
###
from PIL import Image
###
from PIL.Image import Image
###
def testing_decorator():
    pass

@testing_decorator
@testing_decorator(1)
def f():
    pass
###
with open("README.md") as f:
    tellraw @p f.readline()
###
with:
    pass
###
with None:
###
with None as:
###
with None, None, None:
    pass
###
with None as x, None, None as y:
    pass
###
macro foo:
    pass
###
macro foo:
    foo
foo
###
macro foo number=brigadier:integer text=brigadier:string{"type": "greedy"}:
    print(number, text)
foo 42 this is fine really
###
macro foo:
    bar
macro bar:
    foo
###
macro foo:
    macro bar:
        foo
    bar
###
def thing():
    macro bar:
        pass
    bar
bar
###
macro foo:
    macro bar:
        foo
    bar
def thing():
    bar
###
macro foo bar=#brigadier:integer:
    pass
###
macro foo bar=brigadier:does_not_exist:
    pass
###
macro >> message=minecraft:message:
    say message
>> hello @p
###
macro setblock block=minecraft:block_state:
    setblock ~ ~ ~ block
setblock stone
setblock 1 2 3 stone
###
macro do_twice body=mecha:nested_root:
    yield body
    yield body
do_twice:
    say hello
###
macro foo:
    pass
as @p run foo
###
macro foo:
    pass
as @p foo
###
macro execute foo:
    pass
as @p foo
###
macro macro:
    pass
###
macro foo(stream):
    pass
###
macro foo bar(stream):
    pass
###
macro foo(stream):
    pass
macro foo(stream):
    pass
###
macro foo message=minecraft:message(stream):
    pass
###
raise
###
raise ValueError()
###
raise ValueError() from None
###
foo = {
    a: 1,
    "b" + "c": 2
}
###
foo = r""
###
foo = r"\"
###
foo = r"\\"
###
foo = r"\""
###
macro foo(stream):
    with stream.syntax(number=r"\d+", name=r"\w+"):
        stream.expect("number")
        stream.expect("name")
###
class Foo:
    pass
###
class Foo(object):
    pass
###
class A:
    pass
class B:
    pass
class Foo(A, B):
    pass
###
class Foo:
    def bar(self):
        pass
###
class Foo:
    pass
Foo()
###
class Foo:
    bar = 2
print(Foo.bar)
###
class Foo:
    Foo()
###
class Foo:
    bar = 2
print(bar)
###
@print
class Foo:
    pass
###
@print
@str.upper
@str
class Foo:
    pass
###
@print
foo = "bar"
###
@print
###
if True:
    @print
class A:
    pass
###
class Foo:
    def __init__(self, name):
        self.name = name
###
class Foo:
    return
###
def f():
    class Foo:
        return
###
class Foo:
    bar = 1 + 2
###
class Foo:
    say bar
###
class Foo:
    def bar(self):
        say bar
###
class A:
    def b(self):
        say b
        return B()
class B:
    def a(self):
        say a
        return A()
###
if 0:
    import math
###
def f():
    if 0:
        import this
###
for i in range(10):
    if i % 2 == 0:
        from math import sin
###
if "beans":
    macro beans:
        pass
###
for bean in "beans":
    if bean:
        macro jelly bean(stream):
            pass
###
class A:
    macro foo:
        pass
###
class B:
    import math
###
particle minecraft:dust 0.00000 (117/255) (164/255) 0.5 ~ ~ ~ 0 0 0 0 1 force @s
