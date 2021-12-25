import sys
###
def f():
    pass
f.__code__
###
def hello():
    return "world"
say hello.__name__.capitalize()
###
from runtime import ctx
###
print(f'foo {str.__name__} bar')
###
"a{0.__class__}b".format(42)
###
foo = "a{x.__class__}b".format_map({"x":42})
###
from runtime import current_path
say current_path.format()
