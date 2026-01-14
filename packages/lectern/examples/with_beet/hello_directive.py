""" "Plugin that defines the `@hello <name>` directive."""

from beet import Context, DataPack, Function, ResourcePack

from lectern import Document, Fragment


def beet_default(ctx: Context):
    document = ctx.inject(Document)
    document.directives["hello"] = hello


def hello(fragment: Fragment, assets: ResourcePack, data: DataPack):
    name = fragment.expect("name")
    function = data.functions.setdefault("hello:greetings", Function([]))
    function.lines.append(f"say Hello, {name}!")
