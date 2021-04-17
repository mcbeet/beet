#!set obj1 = ctx.generate.objective()
#!set obj2 = ctx.generate.objective("foo")

scoreboard players operation @s {{ obj1 }} += @s {{ obj2 }}

#!set generate = ctx.generate["thing"]
#!set obj1 = generate.objective()
#!set obj2 = generate.objective("foo")

scoreboard players operation @s {{ obj1 }} += @s {{ obj2 }}
