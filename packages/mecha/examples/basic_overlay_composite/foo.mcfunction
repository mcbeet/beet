scoreboard objectives add roll_dice dummy
# scoreboard objectives setdisplay belowName roll_dice
execute store result score @s roll_dice run random value 1..6
