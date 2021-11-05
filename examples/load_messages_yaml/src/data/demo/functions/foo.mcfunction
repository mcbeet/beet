tellraw @a {{ "demo:thing" | msg }}
tellraw @a {{ "demo:multiple" | msg("foo[0]") }}
tellraw @a {{ "demo:multiple" | msg("bar[0]") }}
tellraw @a {{ "demo:multiple" | msg("bar[1]") }}
tellraw @a {{ "demo:multiple" | msg("bar[1].text") }}
