scoreboard objectives add my_consts dummy
scoreboard players set 10 my_consts 10
scoreboard players operation @e[tag=hello,scores={foo=1..}] foo += 10 my_consts
execute if score @s foo matches 20.. as @e[tag=hello] run setblock ~ ~ ~ stone
