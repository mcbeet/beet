from beet import Context
from beet.contrib.vanilla import Vanilla


def beet_default(ctx: Context):
    ctx.inject(Vanilla).mount("assets/minecraft/font", fetch_objects=True)
