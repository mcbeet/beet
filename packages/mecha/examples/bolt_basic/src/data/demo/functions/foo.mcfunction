say hello
say this is a function file augmented with mecha

if score @s tmp matches 1.. as @a:
    for feature in [
        "multiline",
        "nesting",
        "implicit execute",
        "relative location",
    ]:
        say (feature + " is automatically enabled")
    message = "abc" * 5
    say message.upper()

def you_can_make_functions():
    say you_can_make_functions.__name__.replace("_", " ").capitalize()
    tellraw @a [
        "",
        {"text": "yep"},
    ]
    return "and return values"

say you_can_make_functions()

def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

say fib(7)
say fib(8)
say fib(9)

def default_params_are_neat(
    number,
    result=fib(number),
    thing={
        "number": number,
        "result": result,
    },
):
    say Unlike in python default params are evaluated when the function is called
    say number
    say result
    say thing

default_params_are_neat(12)

say this is basically a custom subset of python
say functions are first-class objects just like in python

my_functions = []

for i in "abc":
    def functions_in_loop(value):
        def yo():
            say value.upper()
        return yo
    my_functions.append(functions_in_loop(i * 3))

my_functions[0]()
my_functions[1]()
my_functions[2]()

should_break = False

while True:
    if should_break:
        break
    say just once
    should_break = True

something = '{"text": "Hello", "bold": true}'
as @a at @s if block ~ ~-1 ~ #wool give @s stone{
    display: {
        Name: something
    }
}

with_tuples = ((((())))) + (1,2,3) + (4,)
say with_tuples
say (with_tuples)
say (with_tuples,)
a = f'\\'
say f"f-strings {"work".upper()!r} too {a}"
say f"{{{f"{{{f"{{{7:08}}}\\"}}}\""}}}"

x = 8
if score @s tmp matches (x, None) say wat
if score @s tmp matches f"{x}.." say wat


def copy_items(type, count):
    for i in range(count):
        item replace entity @a f"{type}.{i}" from entity @s f"{type}.{i}"

copy_items('hotbar', 9)
copy_items('inventory', 26)

def f():
    yield 1
    yield 2
    yield 3

for i in f():
    say i

def wow(ok):
    yield from ok()
    yield from ok()

say list(wow(f))

say ctx.generate.id("hello")

import math
say math.cos(math.pi)

import math as m
say (math is m)

from ./thing import do_stuff

say do_stuff(1, math.pi)

import ./thing as thing

say (thing.do_stuff is do_stuff)

for i in range(6):
    if i == 1:
        say 1
    elif i == 2:
        say 2
    elif i == 3:
        say 3
    else:
        say other
    say done

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
    if entity @s[distance=..0.6] function ./abc:
        say foo
        say bar

baz = "demo:xyz"
if predicate foo:bar function baz:
    say foo
    say bar

for node in generate_tree("abcdefghijklmnopqrstuvwxyz0123456789"):
    append function node.parent:
        if node.partition(5):
            if score @s thingy matches node.range function node.children
        else:
            if score @s thingy matches node.range say node.value

data modify entity @e[type=armor_stand,limit=1] NoBasePlate set value 1b

from ./thing import call_recursive
call_recursive()

def try_coordinates():
    a = 1
    setblock a 2 3 stone
    a = "1 2 3"
    setblock a stone
    a = 1
    if block ^ f"^{a}" ^ #planks say 42
    if block ("~", "~", "~") #planks say 42

try_coordinates()

keyword_arguments = dict(foo=1, bar=2, **{"thing": 42})
say keyword_arguments

for node in generate_tree(range(8), name="small_tree"):
    append function node.parent:
        if node.partition():
            if score @s thingy matches node.range function node.children
        else:
            if score @s thingy matches node.range say node.value

def try_unpacking():
    a = [1, *"abc", 2]
    b = dict(zip(a, a))
    c = {**b, "b": "thing"}
    say c

try_unpacking()

def try_set_item():
    try_set_item.data = {}
    try_set_item.data[1] = {}
    try_set_item.data[1][2] = "foo"
    say try_set_item.data

try_set_item()

for node in generate_tree(range(10, 20), key=int):
    append function node.parent:
        if node.partition():
            if score @s thingy matches node.range function node.children
        else:
            if score @s thingy matches node.range say node.value

scoreboard objectives setdisplay list some_score_name
color = "red"
scoreboard objectives setdisplay f"sidebar.team.{color}" some_score_name

weapon = {1: "weapon.offhand", 2: "weapon.mainhand"}
item replace entity @s weapon.offhand from entity @s weapon.mainhand
my_weapon = weapon
item replace entity @s my_weapon.1 from entity @s my_weapon.2

numbers = list(range(12))
say numbers[:]
say numbers[3:]
say numbers[:9]
say numbers[3:9]
say numbers[::]
say numbers[3::]
say numbers[:9:]
say numbers[3:9:]
say numbers[::-1]
say numbers[9::-1]
say numbers[:3:-1]
say numbers[9:3:-1]

execute at @s if block ~ ~ ~ #minecraft:beds:
    teleport @s ~ ~0.56250 ~

del numbers[3:]
say numbers

for loop, value in loop_info("abcd"):
    say f"==[{loop.current}]=="
    say (value == loop.current)
    say loop.before
    say loop.after
    say loop.first
    say loop.last
    say loop.cycle("foo", "bar")

from ./thing import raw

raw(f"say hello{'!' * 5}")

execute function demo:bbb:
    say 1
append function demo:bbb:
    say 2
prepend function demo:bbb:
    say 0

mykey1 = "foo"

if data storage some:path/to/storage f"some.{mykey1}.path"
if data storage some:path/to/storage f"some.{mykey1}.path" run say hi
if data storage some:path/to/storage f'some.{mykey1}.path{{my: "compound"}}'
if data storage some:path/to/storage f'some.{mykey1}.path{{my: "compound"}}' run say hi

mykey2 = "bar"

mypath1 = f"some.{mykey2}.path"
if data storage some:path/to/storage (mypath1)
if data storage some:path/to/storage (mypath1) run say hi

mypath2 = f'some.{mykey2}.path{{my: "compound"}}'
if data storage some:path/to/storage (mypath2)
if data storage some:path/to/storage (mypath2) run say hi

mypath3 = f'some.{mykey2}.path[{{my: "subscript"}}]'
if data storage some:path/to/storage (mypath3)
if data storage some:path/to/storage (mypath3) run say hi

myindex = 42

if data storage some:path/to/storage f'some.{mykey1}.path{{my: "compound"}}.stuff[{myindex}].beep.{mykey2}[{{my: "subscript"}}].boop' run say hi

mypath4 = "foo.bar"
if data storage some:path/to/storage mypath4

if data storage some:path/to/storage "some.foo.path"

import nbtlib
mypath5 = nbtlib.Path().something.cool[3].foo
if data storage some:path/to/storage mypath5

from uuid import UUID

def try_entity_interpolation(x):
    if score x some_objective matches 0 say yes

try_entity_interpolation("some_fake_player")
try_entity_interpolation("0-0-0-0-1")
try_entity_interpolation(UUID("12345678-1234-5678-1234-567812345678"))

entity_type = "creeper"
at @e[type=entity_type] summon lightning_bolt

language minecraft:aaaa {
    "menu.singleplayer": "AAAA"
}

some_translation = "bonjour"

merge language minecraft:aaaa {
    "something.else": some_translation
}

merge language minecraft:aaaa:
    yaml.key1: some_translation.upper()
    yaml.key2: some_translation.title()

x = 0
y = 1
z = 2

data merge storage demo:foo:
    custom_data1: [x, y, z]
    custom_data2:
        -   x
        -   y
        -   z

def set_at_origin(block):
    setblock 0 0 0 block

set_at_origin(minecraft:stone)

some_name = ./useless/../no_quotes_lol
function some_name:
    say that's neat

if ./a/b/c == ./x/../a/b/x/../c:
    say same thing

tellraw @a:
    text: 'hello world'

function_tag felix:howdy:
    values: ['demo:foo', __name__]

execute at @s run particle minecraft:dust 0 1 1 0.9 ~ ~1 ~ 0 0 0 0.01 1 force
execute at @s run particle minecraft:block yellow_concrete ~ ~1.62 ~ 0 0.4 0 0 30 force
execute at @s run particle minecraft:block minecraft:light_blue_concrete ~ ~1 ~ 0.05 0.1 0.05 0 3

particle_file minecraft:end_rod {
  "textures": [
    "minecraft:glitter_7",
    "minecraft:glitter_6",
    "minecraft:glitter_5",
    "minecraft:glitter_4",
    "minecraft:glitter_3",
    "minecraft:glitter_2",
    "minecraft:glitter_1",
    "minecraft:glitter_0"
  ]
}

for obj in ["foo", "bar"]:
    as @a[scores={obj=1..}] scoreboard players remove @s obj 1

x = 8
scoreboard players set @p tmp -x

x = 12
y = 23
z = 34

tp @s f"~{x} ~{y} ~{z}"
tp @s f"~{x}" y f"~{z}"

tp @s x y z
tp @s ~x ~y ~z
tp @s ^x ^y ^z
tp @s -x -y -z
tp @s ~-x ~-y ~-z
tp @s ^-x ^-y ^-z

for i, x in enumerate("abc"):
    say f"{i} {x}"

major, minor, patch = "1.2.3".split(".")
say major
say minor
say patch

def check_above(n):
    if n > 0:
        if block ~ ~n ~ air:
            check_above(n - 1)
    else:
        say nothing above!

check_above(6)

math = 0
say math
def wat():
    global math
    import math
wat()
say math.ceil(0.1)

say bolt implements a __rebind__(rhs) magic method that gets called when you reassign a value to a variable
say let's try it out by manually building a class

def init_global_score(self, name):
    self.name = name

def add_global_score(self, rhs):
    tmp = GlobalScore(generate_id("tmp.{incr}"))
    scoreboard players operation tmp.name global = self.name global
    tmp += rhs
    return tmp

def iadd_global_score(self, rhs):
    if isinstance(rhs, GlobalScore):
        scoreboard players operation self.name global += rhs.name global
    else:
        scoreboard players add self.name global rhs
    return self

def rebind_global_score(self, rhs):
    if self is not rhs:
        if isinstance(rhs, GlobalScore):
            scoreboard players operation self.name global = rhs.name global
        else:
            scoreboard players set self.name global rhs
    return self

GlobalScore = type("GlobalScore", (), {
    "__init__": init_global_score,
    "__add__": add_global_score,
    "__iadd__": iadd_global_score,
    "__rebind__": rebind_global_score,
})

a = GlobalScore("a")
a = 123
a = 456

b = GlobalScore("b")
b = 789
b = a

a += b + 6 + a
b += 1

say you can use nonlocal to create fake classes

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

def foo(msg):
    say msg

if score #temp abc matches 1..:
    foo("foo")

tag_name = ./yolo_funcs

function_tag tag_name:
    values:
        -   "demo:foo"

as @p function #tag_name # this runs the tag

def truth_table():
    for a in [False, True]:
        for b in [False, True]:
            for c in [False, True]:
                for d in [False, True]:
                    yield (a and b or c and not d) in [True] not in [False]

say list(truth_table())

def not_init(self, value):
    self.value = value

def not_not(self):
    say self.value
    return self

NotPrint = type("NotPrint", (), {"__init__": not_init, "__not__": not_not})
not not not not NotPrint("hello")

def thing_within(self, container):
    for item in container:
        say (self == item)
    return self

def thing_contains(self, item):
    say (self == item)
    return self

def thing_equal(self, item):
    return f"thing == {item}"

Thing = type("Thing", (), {"__within__": thing_within, "__contains__": thing_contains, "__eq__": thing_equal})
Thing() in [1, 2, 3] in [99]
"world" in ("hello" in Thing())

from contextlib import contextmanager

def dsl_init(self, score, inverted=False):
    self.score = score
    self.inverted = inverted

def dsl_not(self):
    return DSL(self.score, not self.inverted)

def dsl_branch(self):
    if score @s self.score matches int(not self.inverted):
        yield True

DSL = type("DSL", (), {"__init__": dsl_init, "__not__": dsl_not, "__branch__": contextmanager(dsl_branch)})

if DSL("foo"):
    say yes
    if DSL("bar"):
        say with bar
else:
    say no

predicate ./check_scores [
  {
    "condition": "minecraft:entity_scores",
    "entity": "this",
    "scores": {
      "foo": 1
    }
  },
  {
    "condition": "minecraft:entity_scores",
    "entity": "killer_player",
    "scores": {
      "bar": 1
    }
  }
]

def cond_init(self, name=generate_id("tmp{incr}")):
    self.name = name

def cond_str(self):
    return self.name

def cond_not(self):
    result = Cond()
    result = 1
    unless score global self matches 0:
        result = 0
    return result

def cond_dup(self):
    result = Cond()
    result = self
    return result

def cond_rebind(self, rhs):
    if isinstance(rhs, Cond):
        scoreboard players operation global self = global rhs
    else:
        scoreboard players set global self rhs
    return self

def cond_branch(self):
    unless score global self matches 0:
        yield True

Cond = type("Cond", (), {
    "__init__": cond_init,
    "__str__": cond_str,
    "__not__": cond_not,
    "__dup__": cond_dup,
    "__rebind__": cond_rebind,
    "__branch__": contextmanager(cond_branch),
})

is_awesome = Cond("is_awesome")
is_awesome = Cond("is_cool") and Cond("is_nice")

if is_awesome or Cond("force_awesomeness"):
    say hello
