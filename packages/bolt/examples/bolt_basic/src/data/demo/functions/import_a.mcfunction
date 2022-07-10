from bolt import Runtime

runtime = ctx.inject(Runtime)

foo = 42

def callback():
    return foo

def loga(f):
    runtime.modules.get().namespace["bar"] *= 2
    say __name__
    say runtime.modules.path
    say f()

from ./import_b import logb

logb(callback)
