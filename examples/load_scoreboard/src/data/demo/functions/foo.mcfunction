#!set obj1 = generate_objective()
#!set obj2 = generate_objective("foo")

scoreboard players operation @s {{ obj1 }} += @s {{ obj2 }}

#!set generate = ctx.generate["thing"]
#!set obj1 = generate.objective()
#!set obj2 = generate.objective("foo")

scoreboard players operation @s {{ obj1 }} += @s {{ obj2 }}
