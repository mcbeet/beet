say "🗡 "
tellraw @a {text: "🗡"}


recipe example:sharp_diamond {
    "type":"minecraft:crafting_shapeless",
    "ingredients":[["minecraft:diamond"]],
    "result":{
        "id":"minecraft:diamond",
        "components":{"minecraft:item_name":"🗡"}
    }
}
TEAM_1 = "duels.team_1"
TEAM_2 = "duels.team_2"

execute function ./load:
    team add TEAM_1 "Duels Team 1"
    team add TEAM_2 "Duels Team 2"
    
    for team in [TEAM_1, TEAM_2]:
        team modify team friendlyFire false
        team modify team prefix "🗡 "
        team modify team seeFriendlyInvisibles false

