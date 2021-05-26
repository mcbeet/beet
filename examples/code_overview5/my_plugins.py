from beet import Context, Function, Language


def add_greeting_translations(ctx: Context):
    ctx.assets["minecraft:en_us"] = Language({"greeting.hello": "hello"})
    ctx.assets["minecraft:fr_fr"] = Language({"greeting.hello": "bonjour"})


def add_greeting(ctx: Context):
    ctx.require(add_greeting_translations)
    greeting_count = ctx.meta["greeting_count"]

    ctx.data["greeting:hello"] = Function(
        ['tellraw @a {"translate": "greeting.hello"}'] * greeting_count,
        tags=["minecraft:load"],
    )
