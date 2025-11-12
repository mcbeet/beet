from bolt import Runtime

runtime = ctx.inject(Runtime)

bar = 7

def callback():
    return bar

def logb(f):
    runtime.modules.current.namespace["foo"] *= 2
    say __name__
    say runtime.modules.current_path
    say f()

from ./import_a import loga

loga(callback)
