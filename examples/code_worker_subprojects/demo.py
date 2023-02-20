from typing import List, Optional

from beet import Connection, Context, DataPack, Mcmeta, subproject


def bridge(connection: Connection[Optional[Mcmeta[DataPack]], Mcmeta[DataPack]]):
    q: List[Mcmeta[DataPack]] = []

    for client in connection:
        for mcmeta in client:
            if mcmeta:
                q.append(mcmeta)
            else:
                for mcmeta in q:
                    client.send(mcmeta)
                q = []


def export_mcmeta(ctx: Context):
    with ctx.worker(bridge) as channel:
        # Send the mcmeta file to the worker
        channel.send(ctx.data.mcmeta)


def beet_default(ctx: Context):
    for lib in sorted(ctx.directory.glob("lib_*")):
        config = {
            "data_pack": {
                "load": [lib.name],
            },
            "pipeline": ["demo.export_mcmeta"],
        }
        ctx.require(subproject(config))

    with ctx.worker(bridge) as channel:
        # Request mcmeta files from the worker
        channel.send(None)

    final_mcmeta = Mcmeta[DataPack](
        {
            "pack": {
                "pack_format": 7,
                "description": "This is the root",
            },
            "custom_data": 0,
            "libs": [],
        }
    )

    for mcmeta in channel:
        final_mcmeta.data["custom_data"] += mcmeta.data["custom_data"]
        final_mcmeta.data["libs"].append(mcmeta.data)

    ctx.data.mcmeta = final_mcmeta
