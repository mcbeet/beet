from ./util import repeat, lisp

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

lisp foo
lisp 123
lisp (foo 123)
lisp (foo 123 () (bar))
lisp (
    (defun do_math (x y)
        (add x y))
    (defun do_more_math (x y)
        (mul (do_math x y) y))
)
