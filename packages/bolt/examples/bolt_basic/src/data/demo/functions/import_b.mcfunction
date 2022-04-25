from bolt import Runtime

runtime = ctx.inject(Runtime)

bar = 7

def callback():
    return bar

def logb(f):
    runtime.get_module().namespace["foo"] *= 2
    say __name__
    say runtime.get_path()
    say f()

from ./import_a import loga

loga(callback)
