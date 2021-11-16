execute if score @p tmp matches 1 run say hello
execute as @a at @s run setblock ~ ~ ~ stone
execute if score @p tmp matches 1 say hello
execute as @a at @s setblock ~ ~ ~ stone
if score @p tmp matches 1 run say hello
as @a at @s run setblock ~ ~ ~ stone
if score @p tmp matches 1 say hello
as @a at @s setblock ~ ~ ~ stone

execute store result score PLAYER_COUNT global if entity @a
store result score PLAYER_COUNT global if entity @a
