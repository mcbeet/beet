from beet import Context, Function, configurable
from beet.core.utils import JsonDict


def beet_default(ctx: Context):
    ctx.require(
        demo_thing1,
        demo_thing2,
        demo_thing3,
    )


@configurable("demo.thing1")
def demo_thing1(ctx: Context, opts: JsonDict):
    ctx.generate(Function([f"# thing1 {opts}"]))


@configurable("demo.thing2")
def demo_thing2(ctx: Context, opts: JsonDict):
    ctx.generate(Function([f"# thing2 {opts}"]))


@configurable("demo.thing3")
def demo_thing3(ctx: Context, opts: JsonDict):
    ctx.generate(Function([f"# thing3 {opts}"]))
