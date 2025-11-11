loot_table demo:bar {
    "pools": [
        {
            "rolls": 1,
            "entries": [
                {
                    "type": "item",
                    "name": "minecraft:emerald",
                    "functions": [
                        {
                            "function": "minecraft:set_nbt",
                            "tag": "{ \
                                custom: { \
                                    item: '$PLACEHOLDER', \
                                    json_text_component: '{ \
                                        \"text\": \"nonsense\", \
                                        \"color\": \"aqua\", \
                                        \"function\": \"minecraft:set_nbt\", \
                                        \"tag\": \"{who_cares: \\'$PLACE\
                                                                        HOLDER\\'}\" \
                                    }' \
                                } \
                            }"
                        }
                    ]
                }
            ]
        }
    ]
}
