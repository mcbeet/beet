from beet import Context
from beet.contrib.vanilla import Vanilla


def beet_default(ctx: Context):
    vanilla = ctx.inject(Vanilla)
    print(vanilla.assets.textures.get("minecraft:block/stone"))
