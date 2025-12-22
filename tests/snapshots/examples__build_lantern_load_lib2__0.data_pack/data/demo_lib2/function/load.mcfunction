execute unless score demo_lib1.major load.status matches 42.. run say demo_lib2: missing dependency demo_lib1==42..
execute if score demo_lib1.major load.status matches 42.. run scoreboard players set demo_lib2.major load.status 7
execute if score demo_lib2.major load.status matches 7 run function #demo_lib2:init
