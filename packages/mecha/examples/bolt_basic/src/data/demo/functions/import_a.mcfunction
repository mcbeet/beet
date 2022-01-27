from mecha.contrib.bolt import Runtime

runtime = ctx.inject(Runtime)

foo = 42

def callback():
    return foo

def loga(f):
    runtime.get_module().namespace["bar"] *= 2
    say __name__
    say runtime.get_path()
    say f()

from ./import_b import logb

logb(callback)
