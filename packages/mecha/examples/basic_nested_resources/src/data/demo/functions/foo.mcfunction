function_tag minecraft:tick {
    "values": [
        "demo:foo"
    ]
}

say hello

function demo:bar:
    say world

merge function_tag minecraft:tick {
    "values": [
        "demo:bar"
    ]
}
