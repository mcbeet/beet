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

summon pig
summon pig ~ ~ ~ {Fire:120s}
execute summon pig data merge entity @s {Fire:120s}
execute summon pig:
    data merge entity @s {Fire:120s}

at @a run summon pig
at @a run summon pig ~ ~ ~ {Fire:120s}
at @a summon pig data merge entity @s {Fire:120s}
at @a summon pig:
    data merge entity @s {Fire:120s}
