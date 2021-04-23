#!set obj1 = generate_objective()
#!set obj2 = generate_objective("foo")

scoreboard players operation @s {{ obj1 }} += @s {{ obj2 }}
