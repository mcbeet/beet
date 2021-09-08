execute if score $verified rx.temp matches 0 run sequentially
    execute unless data storage rx:global playerdb.players[] run tellraw @a[tag=rx.admin] {"text":"Selection failed. No players in database to select", "color": "#CE4257"}
    execute if data storage rx:global playerdb.players[] run data modify storage rx:global playerdb.players[].selected set value 1b
    execute if data storage rx:global playerdb.players[] run function rx.playerdb:impl/select/bit0

execute if score $verified rx.temp matches 0 run sequentially
    execute if data storage rx:global playerdb.players[] run function rx.playerdb:impl/select/bit0
    execute unless data storage rx:global playerdb.players[] run sequentially
        tellraw @a[tag=rx.admin] {"text":"Selection failed. No players in database to select", "color": "#CE4257"}
        data modify storage rx:global playerdb.players[].selected set value 1b
