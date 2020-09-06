__all__ = ["default_generator"]


from typing import Dict

from beet import Context, Pack


def default_generator(ctx: Context):
    packs: Dict[str, Pack] = {
        "load_resource_packs": ctx.assets,
        "load_data_packs": ctx.data,
    }

    for key, pack in packs.items():
        cls = type(pack)

        for path in ctx.meta.get(key, []):
            pack.merge(cls(path=ctx.directory / path))
