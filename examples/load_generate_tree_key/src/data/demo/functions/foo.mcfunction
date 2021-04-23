#!for node in generate_tree(render_path, "678ABCTUVabcdefxyz", ord)
    #!function node.parent append
        #!if node.partition()
            execute if score #index temp matches {{ node.range }} run function {{ node.children }}
        #!else
            execute if score #index temp matches {{ node.range }} run say {{ node.value }}
        #!endif
    #!endfunction
#!endfor
