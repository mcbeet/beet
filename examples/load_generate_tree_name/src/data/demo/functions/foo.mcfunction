#!for node in generate_tree("azertyuiop", name="row1")
    #!function node.parent append
        #!if node.partition()
            execute if score #row1 temp matches {{ node.range }} run function {{ node.children }}
        #!else
            execute if score #row1 temp matches {{ node.range }} run say {{ node.value }}
        #!endif
    #!endfunction
#!endfor

#!for node in generate_tree("qsdfghjklm", name="row2")
    #!function node.parent append
        #!if node.partition()
            execute if score #row2 temp matches {{ node.range }} run function {{ node.children }}
        #!else
            execute if score #row2 temp matches {{ node.range }} run say {{ node.value }}
        #!endif
    #!endfunction
#!endfor

#!for node in generate_tree("wxcvbn", name="row3")
    #!function node.parent append
        #!if node.partition()
            execute if score #row3 temp matches {{ node.range }} run function {{ node.children }}
        #!else
            execute if score #row3 temp matches {{ node.range }} run say {{ node.value }}
        #!endif
    #!endfunction
#!endfor
