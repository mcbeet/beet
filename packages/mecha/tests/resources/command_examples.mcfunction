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
# execute
execute align yxz run spawnpoint @p ~ ~ ~
execute anchored eyes run tp ^ ^ ^
execute anchored eyes run tp ^5 ^ ^
execute as @e[type=sheep] run data get entity @s
execute as @e[type=villager] run data merge entity @s {Invulnerable: 1}
execute as @e[type=sheep] at @s run tp ~ ~1 ~
execute at @e[type=sheep] run kill @s
execute facing ^1 ^ ^ run tp ~ ~ ~
execute as @e at @s facing 0 64 0 run tp @s ^ ^ ^1
execute as @e at @s facing 0 64 0 run tp @s ^ ^ ^1 ~ ~
execute as @e[type=!player] at @s facing entity @p feet run tp @s ^ ^ ^1
execute in the_end run locate structure endcity
execute in minecraft:the_nether positioned as @s run tp ~ ~ ~
execute in minecraft:the_nether run tp ~ ~ ~
execute in minecraft:the_nether run tp ~ ~ ~5
execute positioned 0 64 0 run locate structure village
execute as @e[type=sheep] at @s rotated as @p run tp @s ^ ^ ^1
execute as @e[type=sheep] positioned as @s rotated as @p run tp @s ^ ^ ^1
execute as @a at @s if block ~ ~-1 ~ #wool run kill @s
execute if score @s A = @s B
execute as @a if data entity @s Inventory[{Slot: 0b}].tag.Enchantments[{id: "minecraft:efficiency"}] run tp @s 0 64 0
execute as @a at @s anchored eyes run particle smoke ^ ^ ^3
execute as @e[type=pig] at @s store success entity @s Saddle byte 1 if entity @p[distance=..5]
execute as @a at @s if block ~ ~ ~ water run say "My feet are soaked!"
execute as @a unless score @s test = @s test run say "Score is reset"
execute at @p as @e[type=pig,distance=..3] run data merge entity @s {Motion: [0.0d, 2.0d, 0.0d]}
execute as @p at @s run teleport @s ~ ~ ~ ~10 ~
execute in minecraft:the_nether run teleport ~ ~ ~
execute as @a in minecraft:the_end run teleport 84 57 79
execute as Alice in minecraft:overworld run teleport 251 64 -160
execute store result score #temp global run data get storage global foo
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
locate structure mansion
# msg
msg @a Hi
# particle
particle dust 1.0 0.5 0.5 1.0
particle dust_color_transition 1.0 0.0 0.0 1.0 0.0 0.0 1.0
particle block minecraft:grass_block[snowy=true]
particle falling_dust minecraft:grass_block[snowy=true]
particle item minecraft:apple
particle vibration 5.0 64.0 0.0 200
particle vibration 5.0 64.0 0.0 200 ^ ^ ^3
particle sculk_charge 1.5707
particle shriek 100
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
# other
scoreboard players operation #sie_1_flags_delta integer = #sie_1_flags integer
scoreboard players set ✔ foo 42
execute at @e[type=armor_stand,name="ctf",tag=!FlagBearer] run particle block_marker barrier ~ ~.8 ~ 0 0 0 0 1 force
execute store result score @s smithed.data run clear @s #smithed:crafter/all 0
execute if entity @s[distance=..0.00000001] run function demo:foo
place template minecraft:fossil/spine_1 ~ ~ ~
place template minecraft:fossil/spine_1 ~ ~ ~ 180
place template minecraft:fossil/spine_1 ~ ~ ~ clockwise_90 left_right
place template minecraft:fossil/spine_1 ~ ~ ~ none front_back 0.5
place template minecraft:fossil/spine_1 ~ ~ ~ counterclockwise_90 none 0.6 42
# 23w06a
execute on vehicle at @s if loaded ~10 ~ ~ run tp @s ~10 ~ ~
execute if biome ~10 ~ ~ minecraft:plains run say ok
execute if dimension minecraft:overworld run say ok
execute unless loaded ~ ~ ~ run say ok
execute unless biome ~10 ~ ~ minecraft:forest run say ok
execute unless dimension minecraft:overworld run say ok
fillbiome ~ ~ ~ ~16 ~16 ~16 minecraft:deep_dark
gamemode survival @a
gamerule blockExplosionDropDecay true
gamerule commandModificationBlockLimit 1000
gamerule globalSoundEvents false
gamerule lavaSourceConversion true
gamerule mobExplosionDropDecay true
gamerule snowAccumulationHeight 10
gamerule tntExplosionDropDecay true
gamerule waterSourceConversion true
clone ~ ~ ~ ~10 ~10 ~10 0 0 0 masked
clone from overworld ~ ~ ~ ~10 ~10 ~10 0 0 0 masked
clone ~ ~ ~ ~10 ~10 ~10 to nether 0 0 0 masked
clone from overworld ~ ~ ~ ~10 ~10 ~10 to nether 0 0 0 masked
data modify block ~ ~ ~ Name set string storage test:main value 0 1
data modify block ~ ~ ~ Name append string block ~ ~1 ~ value 0 1
data modify block ~ ~ ~ Name prepend string entity @s EntityName 0 1
data modify block ~ ~ ~ Name insert 0 string storage test:main value 0 1
data modify block ~ ~ ~ Name merge string storage test:main value 0 1
title @s times 0.5s 10t 1d
weather clear 10t
weather rain 0.235s
weather thunder 1d
ride @s mount @e[type=pig,limit=1,sort=nearest]
ride @s dismount
execute if score @s abc matches 0 run ride @s dismount
execute positioned over ocean_floor run summon skeleton
execute \
    as @a[ \
        tag=blob \
    ] \
    run \
        function demo:foo
s\
a\
y \
h\
e\
l\
l\
o
execute if function demo:foo run return run function demo:bar
execute store result score @s foo run return run data get entity @s foodSaturationLevel
gamerule maxCommandForkCount 9999
scoreboard objectives modify foo displayautoupdate true
scoreboard objectives modify foo numberformat styled {"bold": true}
give @s wooden_pickaxe[damage=23]
give @s wooden_pickaxe[damage=23]{foo: 123}
give @s netherite_hoe[damage=5,repair_cost=2]
give @s stick{foo:'bar'}
give @s stick[custom_data={foo:'bar'}]
clear @s diamond_pickaxe[damage=0]
give @s diamond_sword[enchantment_glint_override=true]
execute as @a if items entity @s weapon.mainhand potion run item modify entity @s weapon.mainhand betterpotions:stack_4
execute as @a if items entity @s player.cursor potion run item modify entity @s player.cursor betterpotions:stack_4
clear @s stick{a:2}
clear @s stick[custom_data~{a:2}]
clear @s *[!damage|damage=0]
clear @s *[count~{max:2}]
clear @s *[damage~{durability:{min:3}}]
clear @s *[custom_data~{gm4_metallurgy: {stored_shamir: "lumos"}}, damage | !max_item_stack=1]
execute if predicate {condition: weather_check, raining: true}
particle minecraft:block{block_state: {Name: "minecraft:redstone_lamp", Properties: {lit: "true"}}}
clear @s *[custom_data~{gm4_metallurgy: {stored_shamir: "lumos"}}, damage | !max_item_stack=1]
execute if predicate {condition: weather_check,raining: true}
particle minecraft:block{block_state: {Name: "minecraft:redstone_lamp",Properties: {lit: "true"}}}
