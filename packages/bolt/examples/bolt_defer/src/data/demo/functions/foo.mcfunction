from mecha import AstString
from bolt.contrib.defer import Defer, AstDefer

defer = ctx.inject(Defer)

counter = 0
def foo():
    global counter
    say counter
    counter += 1

say start
foo()
foo()
defer(foo)
defer(foo)
say end

counter = 7

@defer
def bar():
    function ./bar:
        defer(foo)
        global counter
        counter *= 2

def format_deferred_tag():
    return AstString(value=f"thing{counter}")

tag @p add AstDefer(callback=format_deferred_tag)
