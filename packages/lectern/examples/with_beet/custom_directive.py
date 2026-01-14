from beet import Context, DataPack, ResourcePack
from beet.library.data_pack import Function

from lectern import Document, Fragment


def beet_default(ctx: Context):
    ctx.inject(Document).directives["custom_directive"] = custom_directive


def custom_directive(fragment: Fragment, assets: ResourcePack, data: DataPack):
    function_name, num1, num2 = fragment.expect("function_name", "num1", "num2")
    function = fragment.as_file(Function)
    function.lines *= int(num1) + int(num2)
    data[function_name] = function
