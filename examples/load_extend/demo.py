from typing import Any, ClassVar, Tuple, cast

from pydantic import BaseModel

from beet import Context, JsonFile, JsonFileBase, TextFile, TextFileBase, YamlFileBase
from beet.core.utils import JsonDict


class FunctionConfig(YamlFileBase[JsonDict]):
    scope: ClassVar[Tuple[str, ...]] = ("functions",)
    extension: ClassVar[str] = ".yml"


class BlueprintData(BaseModel):
    name: str


class Blueprint(JsonFileBase[BlueprintData]):
    scope: ClassVar[Tuple[str, ...]] = ("blueprints",)
    extension: ClassVar[str] = ".json"


def extend_data_pack(ctx: Context):
    ctx.data.extend_extra["myproject.json"] = JsonFile
    ctx.data.extend_namespace.append(FunctionConfig)
    ctx.data.extend_namespace.append(Blueprint)
    ctx.data.extend_namespace_extra["numbers.txt"] = TextFile


def process_functions(ctx: Context):
    project_data = cast(JsonFileBase[Any], ctx.data.extra["myproject.json"]).data

    for prefix, dirs, functions in ctx.data.functions.walk():
        dirs.discard("zprivate")

        namespace = ctx.data[prefix.partition(":")[0]]
        numbers = cast(
            TextFileBase[Any], namespace.extra["numbers.txt"]
        ).text.splitlines()

        folder_config = ctx.data[FunctionConfig][prefix + "config"].data

        for function in functions.values():
            function.prepend(
                [
                    f"# config.yml = {folder_config}",
                    f"# numbers.txt = {numbers}",
                    f"# myproject.json = {project_data}",
                ]
            )

    del ctx.data.extra["myproject.json"]
    for namespace in ctx.data.values():
        del namespace.extra["numbers.txt"]
        del namespace[FunctionConfig]

    ctx.data.mcmeta.data["blueprints"] = {
        k: v.data.dict() for k, v in ctx.data[Blueprint].items()
    }

    ctx.data[Blueprint].clear()
