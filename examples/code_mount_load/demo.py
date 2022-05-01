from beet import Context
from beet.contrib.load import load


def beet_default(ctx: Context):
    ctx.require(
        load(
            data_pack={
                "data/demo/functions": ctx.directory / "src",
                "data/owo/functions/foo.mcfunction": ctx.directory / "src/thing.txt",
                "pack.mcmeta": ctx.directory / "pack.mcmeta",
            },
            resource_pack={
                "assets/minecraft": ctx.directory / "src",
                "assets/other/sounds.json": ctx.directory / "src/sounds.json",
                "not_in_schema.txt": ctx.directory / "pack.mcmeta",
            },
        )
    )
