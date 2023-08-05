execute as @p at @s run function demo:beep {name: "steve"}:
    $say hello $(name)
    $execute positioned ~ ~1 ~ run function demo:bop {name: "$(name)"}

function demo:bop:
    $say bye $(name)
