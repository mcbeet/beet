from mecha import AstCommand, AstChildren
from bolt import Runtime

macro repeat n=brigadier:integer command=subcommand:
    execute:
        for _ in range(n.value):
            yield command

repeat 2 as @a run repeat 3 say ok
repeat 3 say world

n = 1
repeat n if score foo bar matches 1 say over!

macro as at
    targets=minecraft:entity{"type": "entities", "amount": "multiple"}
    clause=subcommand{"redirect": ["execute"]}:
    as targets at @s:
        yield AstCommand(identifier="execute:subcommand", arguments=AstChildren([clause]))

as at @e[type=pig] if block ~ ~ ~ water say blbllblb
as at @e[type=bat] setblock ~ ~ ~ lava
if score foo bar matches 1 run as at @e[type=chicken] kill @e[type=fox, distance=..4]

macro execute as at
    targets=minecraft:entity{"type": "entities", "amount": "multiple"}
    clause=subcommand{"redirect": ["execute"]}:
    runtime = ctx.inject(Runtime)
    with runtime.scope() as commands:
        as at targets:
            yield AstCommand(identifier="execute:subcommand", arguments=AstChildren([clause]))
    return commands[0].arguments[-1]

if score foo bar matches 1 as at @e[type=chicken] kill @e[type=fox, distance=..4]
