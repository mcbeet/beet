from mecha.contrib.scripting import Runtime
runtime = ctx.inject(Runtime)
def loga():
    say __name__
    say runtime.get_path()
from ./import_b import logb
logb()
