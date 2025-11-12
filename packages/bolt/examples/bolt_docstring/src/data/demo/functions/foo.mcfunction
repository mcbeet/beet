value = """
    hello
    world
"""

say repr(value)

def f():
    """My function"""
    return 42

say f()
say f.__doc__

def g(a=123):
    """My other function"""
    return a

say g()
say g.__doc__

class A:
    """This is a class.

    It doesn't do anything.
    """

say repr(A.__doc__)

value = r"""
    foo\n\nbar
"""

say repr(value)
