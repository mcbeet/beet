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
-2 ** 3 + ~4 * 5 // 6 / 7 % 9 + 10 - 11 << 12 >> 13 & 14 ^ 15 | 16
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
    thing += bar()
def bar():
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
predicate = {
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
predicate = {
  condition: "minecraft:entity_scores",
  entity: "this",
  scores: {
    score1: {
      "min": {
        "type": "minecraft:score",
        target: "this",
        score: "score2",
        scale: 1
      }
    }
  }
}
###
def f():
    return {f(): f(), other: [{}, {}, "wat"]}
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
    function node.parent append:
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
