from typing import List

from beet import Context, Function, PluginOptions, configurable
from beet.core.utils import JsonDict


def beet_default(ctx: Context):
    ctx.require(plugin1)
    ctx.require(plugin1(commands=["say inline options"]))
    ctx.require(plugin3)
    ctx.require(plugin3(commands=["say blah"]))

    preset = plugin5(foo=1, bar=2)(something=42)
    ctx.require(preset(hello="world"))


@configurable
def plugin1(ctx: Context, opts: JsonDict):
    ctx.generate("plugin1_{incr}", Function(opts["commands"]))


@configurable("different_name")
def plugin2(ctx: Context, opts: JsonDict):
    ctx.generate("plugin2_{incr}", Function(opts["commands"]))


class TestOptions(PluginOptions):
    commands: List[str]


@configurable(validator=TestOptions)
def plugin3(ctx: Context, opts: TestOptions):
    ctx.generate("plugin3_{incr}", Function(opts.commands))


@configurable("something_else", validator=TestOptions)
def plugin4(ctx: Context, opts: TestOptions):
    ctx.generate("plugin4_{incr}", Function(opts.commands))


@configurable
def plugin5(ctx: Context, opts: JsonDict):
    ctx.generate(Function([f"say {opts}"]))
