execute as @p at @s run function demo:beep {name: "steve", offset: 1.3f}:
    execute positioned ~ ~1 ~ run summon creeper
    $say hello $(name)
    $execute as @a[name=$(name)] run say something
    $execute positioned ~ ~$(offset) ~ run function demo:bop {name: "$(name)"}

function demo:bop:
    $say bye $(name)
