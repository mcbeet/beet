scoreboard players set @a foo 1
say @a[scores={thing=..9}]
execute if score @s wat matches 7 run scoreboard players operation @s wat = @p[tag=target,scores={wow=1..},sort=nearest] wow
