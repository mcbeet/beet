from mecha import AstCommand, AstChildren
from bolt import Runtime

runtime = ctx.inject(Runtime)

macro foo:
    say macro foo

foo

macro foo bar=brigadier:integer:
    if bar.value > 0:
        say f"macro foo {bar.value}"
        foo (bar.value - 1)
    else:
        foo

foo 4

macro foo bar=brigadier:integer double:
    foo (bar.value * 2)

foo 3 double

macro foo bar=brigadier:integer message=minecraft:message:
    foo bar
    say message

foo 3 hello @a[
    scores = {
        x = 42
    }
]

macro setblock:
    setblock air
macro setblock block=minecraft:block_state:
    setblock ~ ~ ~ block
macro setblock pos=minecraft:block_pos:
    setblock pos air

setblock
setblock stone
setblock 1 2 3
setblock 1 2 3 stone

macro do_twice body=mecha:nested_root:
    yield body
    return body

do_twice:
    say this is repeated twice

macro >> text=brigadier:string{"type": "greedy"}:
    tellraw @p {"text": text.value}

>> Custom symbols work
as @a run >> Even inside execute

macro execute >> text=brigadier:string{"type": "greedy"}:
    with runtime.scope() as subcommand:
        >> text
    return AstCommand(identifier="execute:run:subcommand", arguments=AstChildren(subcommand))

as @a >> Overload execute to allow implicit "run"

macro tellraw
    targets=minecraft:entity{
        "type": "players",
        "amount": "multiple"
    }
    from
    path=minecraft:resource_location:
    tellraw targets {"text": f"from {path.get_canonical_value()}"}

tellraw @s from ./dummy_message

macro ! targets=minecraft:entity{"type": "entities", "amount": "multiple"} !:
    macro rip:
        kill targets
    def do_it():
        rip
    do_it()

! @e !

macro abc num1=brigadier:integer:
    macro def num2=brigadier:integer:
        say num2
    def num1

abc 42
