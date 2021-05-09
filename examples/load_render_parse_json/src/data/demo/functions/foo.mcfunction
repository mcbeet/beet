#!set message = parse_json('{"text":"edrfghj","color":"dark_aqua"}')
#!do message.update({"bold": True})

tellraw @a {{ message|tojson }}
