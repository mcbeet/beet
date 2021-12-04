say hello
say this is a function file augmented with mecha

if score @s tmp matches 1.. as @a
    for feature in [
        "multiline",
        "nesting",
        "implicit execute",
        "relative location",
    ]
        say (feature + " is automatically enabled")
    message = "abc" * 5
    say message.upper()

def you_can_make_functions()
    say you_can_make_functions.__name__.replace("_", " ").capitalize()
    tellraw @a [
        "",
        {"text": "yep"},
    ]
    return "and return values"

say you_can_make_functions()

def fib(n)
    if n <= 1
        return n
    return fib(n - 1) + fib(n - 2)

say fib(7)
say fib(8)
say fib(9)

def default_params_are_neat(
    number,
    result=fib(number),
    thing={
        "number": number,
        "result": result,
    },
)
    say Unlike in python default params are evaluated when the function is called
    say number
    say result
    say thing

default_params_are_neat(12)

say this is basically a custom subset of python
say functions are first-class objects just like in python

my_functions = []

for i in "abc"
    def functions_in_loop(value)
        def yo()
            say value.upper()
        return yo
    my_functions.append(functions_in_loop(i * 3))

my_functions[0]()
my_functions[1]()
my_functions[2]()

should_break = False

while True
    if should_break
        break
    say just once
    should_break = True
