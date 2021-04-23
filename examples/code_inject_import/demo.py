from dataclasses import dataclass

from beet import Context, Function

HELLO_PATH = f"{__name__}.Hello"
WORLD_PATH = f"{__name__}.World"


@dataclass
class Hello:
    ctx: Context

    def thing(self):
        self.ctx.generate(Function(["say hello"]))


@dataclass
class World:
    ctx: Context

    def thing(self):
        self.ctx.generate(Function(["say world"]))


def beet_default(ctx: Context):
    ctx.inject(HELLO_PATH).thing()
    ctx.inject(WORLD_PATH).thing()
