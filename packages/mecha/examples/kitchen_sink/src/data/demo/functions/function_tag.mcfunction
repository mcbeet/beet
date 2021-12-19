function tag minecraft:tick

say hello

as @a function ./with_tag:
    function tag ./abc
    say world

function ./with_tag append:
    function tag ./xyz

function ./my_load:
    function tag load
    say loaded

function ./also_with_tag:
    say foo
    function tag ./abc
