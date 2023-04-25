def f():
    execute if entity @e[type=pig] run return 123
    n = 77
    execute return n
    return 99999

say f()
