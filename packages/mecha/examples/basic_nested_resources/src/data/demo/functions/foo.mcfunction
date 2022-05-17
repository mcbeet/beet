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

prepend function_tag minecraft:tick {
    "values": [
        "demo:before"
    ]
}

append function_tag minecraft:tick {
    "values": [
        "demo:after"
    ]
}


function_tag demo:abc {
    "values": [
        "demo:foo"
    ]
}

function_tag demo:abc {
    "values": [
        "demo:foo"
    ]
}
