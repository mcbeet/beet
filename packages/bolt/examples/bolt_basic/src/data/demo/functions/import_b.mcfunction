from bolt import Runtime

runtime = ctx.inject(Runtime)

bar = 7

def callback():
    return bar

def logb(f):
    runtime.modules.get().namespace["foo"] *= 2
    say __name__
    say runtime.modules.path
    say f()

from ./import_a import loga

loga(callback)
