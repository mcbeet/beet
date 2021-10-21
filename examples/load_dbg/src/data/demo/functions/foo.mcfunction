#!set foo = generate_objective("foo")

scoreboard players set @p __foo__ 123
say 1
execute if score $size rx.temp matches 1 run data modify storage rx:io playerdb.player set from storage rx:global playerdb.players[{selected: 1b}]
execute if score $size rx.temp matches 1 run data remove storage rx:io playerdb.player.bits
#!dbg score "@p", foo
say hello
execute if score $size rx.temp matches 1 run data modify storage rx:io playerdb.player set from storage rx:global playerdb.players[{selected: 1b}]
execute if score $size rx.temp matches 1 run data remove storage rx:io playerdb.player.bits
say 1
