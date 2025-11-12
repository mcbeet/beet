from ./foo import foo, setblock, do_twice, >>, execute, tellraw, !

foo
foo 4
foo 3 double
foo 3 hello @a[
    scores = {
        x = 42
    }
]

setblock
setblock stone
setblock 1 2 3
setblock 1 2 3 stone

do_twice:
    say this is repeated twice

>> Custom symbols work
as @a run >> Even inside execute
as @a >> Overload execute to allow implicit "run"

tellraw @s from ./dummy_message

! @e !

from ./foo import abc
abc 42
