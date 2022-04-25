from beet import Context, Function

generated_code = """
execute if score #smithed.core load.status matches 1 function ./0:
    data merge storage smithed:log {message:'["Could not find ",{"text":"#smithed.prevent_aggression 0.0.1","color":"red"}]',type:'ERROR'}
    function #smithed:core/pub/technical/tools/log
"""


def beet_default(ctx: Context):
    ctx.data["demo:generated"] = Function(generated_code)
