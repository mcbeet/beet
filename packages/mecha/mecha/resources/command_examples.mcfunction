# advancement
advancement grant @s only minecraft:story/shiny_gear
advancement grant @a everything
# attribute
attribute @s minecraft:generic.armor base set 5
# clear
clear
clear Alice
clear Alice minecraft:wool
clear @p minecraft:golden_sword{Enchantments: [{id: "minecraft:sharpness", lvl: 1s}]}
# data
data get entity @s foodSaturationLevel
data modify entity @e[type=item,distance=..10,limit=1,sort=nearest] PickupDelay set value -1
data get entity @e[type=item,limit=1,sort=random] Pos[1]
data get entity @p Inventory[{Slot: 0b}].id
data modify entity @e[x=0,y=64,z=0,type=dolphin,limit=1] Attributes[{Name: "generic.armor"}].Base set value 20
data modify block 1 64 1 Items[0].id set value "minecraft:diamond_block"
data merge entity @e[type=zombie,limit=1,sort=nearest] {HandDropChances: [0f, 0.8f]}
data modify entity @e[type=zombie,limit=1,sort=nearest] HandDropChances[1] set value 0.8f
# defaultgamemode
defaultgamemode survival
# effect
effect give @s minecraft:resistance 1000000 4 true
effect give @p minecraft:speed 60 1
effect give @p minecraft:speed 60 2
effect clear @a minecraft:haste
effect clear @e[type=zombie]
# enchant
enchant @a infinity
enchant @p sharpness 5
# experience
experience query Steve levels
# fill
fill 52 63 -1516 33 73 -1536 minecraft:gold_block replace minecraft:orange_glazed_terracotta
fill ~-3 ~-3 ~-3 ~3 ~-1 ~3 water
fill ~-3 ~ ~-4 ~3 ~4 ~4 minecraft:stone hollow
fill ~-15 ~-15 ~-15 ~15 ~15 ~15 stone
fill ~-1 ~ ~ ~1 ~ ~ minecraft:prismarine_brick_stairs[facing=south,waterlogged=true]
# function
function custom:example/test
function #custom:example/test
# gamemode
gamemode creative
gamemode survival @a
# gamerule
gamerule doDaylightCycle false
gamerule naturalRegeneration false
gamerule mobGriefing false
gamerule doWeatherCycle false
gamerule keepInventory true
gamerule commandBlockOutput false
gamerule doInsomnia false
# give
give @p minecraft:diamond_sword{display: {Lore: ['"A legendary weapon"']}} 1
give @a potion{Potion: "minecraft:night_vision"} 1
give @r diamond_sword{Enchantments: [{id: "minecraft:sharpness", lvl: 10}]} 1
give @s minecraft:diamond_block{CanPlaceOn: ["minecraft:dirt"]}
give @a potion{Enchantments: [{id: "minecraft:knockback", lvl: 10}], CustomPotionEffects: [{Id: 20, Amplifier: 1}]} 1
# item
item replace block ~ ~2 ~ container.26 with minecraft:spruce_sapling 4
item replace entity @p hotbar.8 with minecraft:spruce_sapling 4
item replace entity @s weapon.offhand from entity @s weapon.mainhand
# kill
kill @s
kill Steve
kill @e[type=item]
kill @e[distance=..10]
kill @e[type=!player]
kill @e[distance=..10,type=creeper]
kill @e[type=arrow,nbt={inBlockState: {Name: "minecraft:target"}}]
# locate
locate mansion
# msg
msg @a Hi
# setblock
setblock ~ ~ ~ chest[facing=east]
setblock ~ ~ ~-1 birch_sign{Text1: '"My chest"', Text2: '"Do not open!"'}
setblock ~ ~2 ~ quartz_slab[type=top]
# spreadplayers
spreadplayers 0 0 200 500 true @a
# summon
summon lightning_bolt ~-10 ~ ~
summon creeper ~ ~ ~ {powered: 1b, CustomName: '{"text":"Powered Creeper"}'}
summon spider ~ ~ ~ {Passengers: [{id: "minecraft:skeleton", HandItems: [{id: "minecraft:bow", Count: 1b}]}]}
summon villager ~ ~ ~ {Offers: {Recipes: [{buy: {id: "dirt", Count: 1}, sell: {id: "diamond", Count: 1}, rewardExp: false}]}}
# teleport
teleport Alice
teleport @a @s
teleport 100 ~3 100
# tellraw
tellraw @a "text to display"
tellraw @a {"text":"I am blue","color":"blue"}
tellraw @a {"text":"I am blue","color":"#5555ff"}
tellraw @a {"text":"Hover me!","hoverEvent":{"action":"show_text","value":"Hi!"}}
tellraw @a "Text1\nText2"
# time
time set 1000t
time set day
time add 24000t
# title
title @a subtitle {"text":"The story begins...","color":"gray","italic":true}
title @a title {"text":"Chapter I","bold":true}
# weather
weather clear 1200
weather rain
