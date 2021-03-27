from PIL import Image

from beet import Context, Function, Texture


def beet_default(ctx: Context):
    ctx.data["basic1:hello"] = Function(["say hello"], tags=["minecraft:load"])
    ctx.assets["minecraft:block/stone"] = Texture(
        Image.new("RGB", (32, 32), color="blue")
    )
