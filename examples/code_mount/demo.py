from beet import Context


def beet_default(ctx: Context):
    ctx.data.mount("data/demo/functions", ctx.directory / "src")
    ctx.data.mount("data/owo/functions/foo.mcfunction", ctx.directory / "src/thing.txt")
    ctx.data.mount("pack.mcmeta", ctx.directory / "pack.mcmeta")
    ctx.assets.mount("assets/minecraft", ctx.directory / "src")
    ctx.assets.mount("assets/other/sounds.json", ctx.directory / "src/sounds.json")
    ctx.assets.mount("not_in_schema.txt", ctx.directory / "pack.mcmeta")
