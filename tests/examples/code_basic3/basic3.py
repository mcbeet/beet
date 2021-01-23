from PIL import Image, ImageDraw

from beet import Context, Function, Texture


def beet_default(ctx: Context):
    ctx.data["basic3:hello"] = Function(["say dirt blinking"], tags=["minecraft:load"])

    image = Image.new("RGB", (16, 32), "green")
    d = ImageDraw.Draw(image)
    d.rectangle([0, 16, 16, 32], fill="yellow")

    ctx.assets["minecraft:block/dirt"] = Texture(
        image, mcmeta={"animation": {"frametime": 20}}
    )
