item modify entity @s armor.feet [{function:"minecraft:set_components",components:{"minecraft:equippable":{slot:"feet",asset_id:"minecraft:netherite"}}}]


execute if predicate [{condition:"minecraft:all_of",terms:[{condition:"minecraft:random_chance",chance:5},{condition:"minecraft:value_check",value:0,range:0}]},{condition:"minecraft:reference",name:"test:l"}] run say aaa