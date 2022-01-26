from mecha.contrib.scripting import Runtime
runtime = ctx.inject(Runtime)
def logb():
    say __name__
    say runtime.get_path()
from ./import_a import loga
loga()
