from beet import Context
from beet.core.utils import TextComponent


def beet_default(ctx: Context):
    description: TextComponent = [
        "override for ",
        {"text": "data pack", "color": "red"},
    ]
    ctx.data.description = description
