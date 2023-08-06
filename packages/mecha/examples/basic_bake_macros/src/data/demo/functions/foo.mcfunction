execute as @p at @s run function demo:beep {name: "steve"}:
    execute positioned ~ ~1 ~ run summon creeper
    $say hello $(name)
    $execute as @a[name=$(name)] run say something
    $execute positioned ~ ~1 ~ run function demo:bop {name: "$(name)"}

function demo:bop:
    $say bye $(name)
