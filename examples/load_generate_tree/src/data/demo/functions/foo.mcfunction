#!function "demo:tick"
#!tag "minecraft:tick"
execute as @a at @s run function demo:foo
#!endfunction

#!set obj = generate_objective("tick")

#!function "demo:start"
scoreboard players set @s {{ obj }} 0
#!endfunction

#!function "demo:stop"
scoreboard players reset @s {{ obj }}
#!endfunction

#!for node in generate_tree("abcdefghijklmnopqrstuvwxyz0123456789")
    #!function node.parent append
        #!if node.partition(5)
            execute if score @s {{ obj }} matches {{ node.range }} run function {{ node.children }}
        #!else
            execute if score @s {{ obj }} matches {{ node.range }} run say {{ node.value }}
        #!endif
    #!endfunction
#!endfor

scoreboard players add @s[scores={ {{ obj }} =0..}] {{ obj }} 1
