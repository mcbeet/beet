from collections import defaultdict
from typing import DefaultDict

from beet import Context, Function, Language


class Internationalization:
    languages: DefaultDict[str, Language]

    def __init__(self, ctx: Context):
        self.languages = defaultdict(Language)
        ctx.require(self.add_translations)

    def add_translations(self, ctx: Context):
        yield
        ctx.assets["minecraft"].languages.merge(self.languages)

    def set(self, key: str, **kwargs: str):
        for code, message in kwargs.items():
            self.languages[code].data[key] = message


def add_greeting(ctx: Context):
    i18n = ctx.inject(Internationalization)
    i18n.set("greeting.hello", en_us="hello", fr_fr="bonjour")

    greeting_count = ctx.meta["greeting_count"]

    ctx.data["greeting:hello"] = Function(
        ['tellraw @a {"translate": "greeting.hello"}'] * greeting_count,
        tags=["minecraft:load"],
    )
