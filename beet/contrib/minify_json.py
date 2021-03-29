"""Plugin that minifies json files."""


import json
from typing import Any, Iterator, Union

from beet import Context, DataPack, JsonFileBase, ResourcePack


def beet_default(ctx: Context):
    for pack in ctx.packs:
        for json_file in find_json_files(pack):
            json_file.text = json.dumps(json_file.data, separators=(",", ":"))


def find_json_files(pack: Union[ResourcePack, DataPack]) -> Iterator[JsonFileBase[Any]]:
    for extra_file in pack.extra.values():
        if isinstance(extra_file, JsonFileBase):
            yield extra_file
    for namespace in pack.values():
        for file_type, container in namespace.items():
            if issubclass(file_type, JsonFileBase):  # type: ignore
                yield from container.values()  # type: ignore
