from ./util import repeat

value = 3

repeat 7:
    value += 1

repeat 3:
    say value

as @a run repeat 3:
    say value

repeat until value < 5:
    say value
    value -= 1

repeat until @a[scores={counter=10}]:
    scoreboard players add @r counter 1
