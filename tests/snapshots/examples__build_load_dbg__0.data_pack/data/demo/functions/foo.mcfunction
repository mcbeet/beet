scoreboard players set @p 5wyugd7r8mxoc 123
say 1
execute if score $size rx.temp matches 1 run data modify storage rx:io playerdb.player set from storage rx:global playerdb.players[{selected: 1b}]
execute if score $size rx.temp matches 1 run data remove storage rx:io playerdb.player.bits
tellraw @a [{"text": "", "hoverEvent": {"action": "show_text", "contents": ["", {"text": "Type: Score\n", "color": "gray"}, {"text": "Path: demo:foo\n\n", "color": "gray"}, "",{"text": "", "extra": [{"text": "", "extra": [{"text": "5", "color": "dark_red"}, {"text": " |  ", "color": "dark_gray"}, {"text": "execute if score $size rx.temp matches 1 run ...\n", "color": "#dddddd"}]}, {"text": "", "extra": [{"text": "6", "color": "dark_red"}, {"text": " |  ", "color": "dark_gray"}, {"text": "execute if score $size rx.temp matches 1 run ...\n", "color": "gray"}]}, {"text": "", "extra": [{"text": "7", "color": "red"}, {"text": " |  ", "color": "dark_gray"}, {"text": "#!dbg score \"@p\", foo\n", "color": "#dddddd"}]}, {"text": "", "extra": [{"text": "8", "color": "dark_red"}, {"text": " |  ", "color": "dark_gray"}, {"text": "say hello\n", "color": "gray"}]}, {"text": "", "extra": [{"text": "9", "color": "dark_red"}, {"text": " |  ", "color": "dark_gray"}, {"text": "execute if score $size rx.temp matches 1 run ...\n", "color": "#dddddd"}]}]},""]}}, {"text": "[load_dbg]: ", "color": "gray"}, {"text": "< @p ", "color": "gold", "extra": ["",{"score": {"name": "@p", "objective": "5wyugd7r8mxoc"}},"", " >"]}]
say hello
execute if score $size rx.temp matches 1 run data modify storage rx:io playerdb.player set from storage rx:global playerdb.players[{selected: 1b}]
execute if score $size rx.temp matches 1 run data remove storage rx:io playerdb.player.bits
say 1
