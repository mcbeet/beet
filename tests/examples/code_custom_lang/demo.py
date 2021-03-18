from beet import Context, Language


def beet_default(ctx: Context):
    ctx.assets.language_config["aaaa"] = {
        "name": "AAAA name",
        "region": "AAAA region",
        "bidirectional": False,
    }

    ctx.assets["minecraft:aaaa"] = Language({"menu.singleplayer": "AAAA"})
