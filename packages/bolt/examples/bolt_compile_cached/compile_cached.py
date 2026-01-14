from beet import Context, sandbox, subproject


def beet_default(ctx: Context):
    ctx.require(sandbox(compile_cached))


def compile_cached(ctx: Context):
    cached_data_pack = ctx.cache["compile_cached"].directory / "data_pack"

    if cached_data_pack.is_dir():
        ctx.data.load(cached_data_pack)
    else:
        ctx.require(
            subproject(
                {
                    "require": ["bolt"],
                    "data_pack": {"load": {"data/demo/functions/cached": "cached"}},
                    "pipeline": ["mecha"],
                }
            )
        )
        ctx.data.save(path=cached_data_pack, overwrite=True)
