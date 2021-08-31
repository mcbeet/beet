defaultgamemode survival
fill 52 63 -1516 33 73 -1536 minecraft:gold_block replace minecraft:orange_glazed_terracotta
fill ~-3 ~-3 ~-3 ~3 ~-1 ~3 water
fill ~-3 ~ ~-4 ~3 ~4 ~4 minecraft:stone hollow
fill ~-15 ~-15 ~-15 ~15 ~15 ~15 stone
fill ~-1 ~ ~ ~1 ~ ~ minecraft:prismarine_brick_stairs[facing=south,waterlogged=true]
function custom:example/test
function #custom:example/test
gamerule doDaylightCycle false
gamerule naturalRegeneration false
gamerule mobGriefing false
gamerule doWeatherCycle false
gamerule keepInventory true
gamerule commandBlockOutput false
gamerule doInsomnia false
locate mansion
msg @a Hi
setblock ~ ~ ~ chest[facing=east]
setblock ~ ~ ~-1 birch_sign{Text1:'"My chest"',Text2:'"Do not open!"'}
setblock ~ ~2 ~ quartz_slab[type=top]
summon lightning_bolt ~-10 ~ ~
summon creeper ~ ~ ~ {powered:1b,CustomName:'{"text":"Powered Creeper"}'}
summon spider ~ ~ ~ {Passengers:[{id:"minecraft:skeleton",HandItems:[{id:"minecraft:bow",Count:1b}]}]}
summon villager ~ ~ ~ {Offers:{Recipes:[{buy:{id:dirt,Count:1},sell:{id:diamond,Count:1},rewardExp:false}]}}
time set 1000
time set day
time add 24000
weather clear 1200
weather rain
