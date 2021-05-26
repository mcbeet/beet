from beet import Context, Function, Language


def add_greeting_translations(ctx: Context):
    ctx.meta["greeting_translations"] = {}

    yield

    for key, translations in ctx.meta["greeting_translations"].items():
        for code, value in translations.items():
            ctx.assets.languages.merge(
                {f"minecraft:{code}": Language({f"greeting.{key}": value})}
            )


def add_greeting(ctx: Context):
    ctx.require(add_greeting_translations)
    greeting_count = ctx.meta["greeting_count"]

    ctx.meta["greeting_translations"]["hello"] = {
        "en_us": "hello",
        "fr_fr": "bonjour",
    }

    ctx.data["greeting:hello"] = Function(
        ['tellraw @a {"translate": "greeting.hello"}'] * greeting_count,
        tags=["minecraft:load"],
    )
