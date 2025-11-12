g_uwu = 1
memo:
    g_uwu = 5
say g_uwu

def ok():
    memo:
        value = 10
    global g_uwu
    g_uwu = value

ok()
say g_uwu

def fib(n):
    if n <= 1:
        return n
    memo n:
        result = fib(n - 1) + fib(n - 2)
    return result

for i in range(50):
    say f"fib({i}) = {fib(i)}"
