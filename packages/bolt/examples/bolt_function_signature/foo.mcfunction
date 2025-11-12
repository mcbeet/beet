def f():
    pass

def f(a):
    pass

def f(a=1):
    pass

def f(a=1,):
    pass

def f(a=1, /):
    pass

def f(a, /, b):
    pass

def f(a=1, /, b=2):
    pass

def f(a=1, /, b=2, *args):
    pass

def f(a, /, b, *, c):
    pass

def f(a=1, /, b=2, *, c=3):
    pass

def f(a=1, /, b=2, *, c=3, **kwargs):
    pass

def f(a=1, /, b=2, *args, c=3, **kwargs):
    pass
