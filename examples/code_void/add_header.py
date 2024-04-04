

from beet import Context, Function



def beet_default(ctx: Context):
    for f in ctx.data.functions.keys():
        ctx.data.functions[f]=Function(f"say {f}")
    
    ctx.data.functions["namespace:"] = Function("give me sugar")
    ctx.data.functions["namespace:a/"] = Function("give me apple")

