from typing import ClassVar, Tuple, cast

from pydantic import BaseModel

from beet import Context, JsonFile, TextFile, YamlFile
from beet.core.file import FileDeserialize, JsonFileBase


class FunctionConfig(YamlFile):
    scope: ClassVar[Tuple[str, ...]] = ("functions",)
    extension: ClassVar[str] = ".yml"


class BlueprintOptions(BaseModel):
    name: str


class Blueprint(JsonFileBase[BlueprintOptions]):
    model = BlueprintOptions

    scope: ClassVar[Tuple[str, ...]] = ("blueprints",)
    extension: ClassVar[str] = ".json"

    data: ClassVar[FileDeserialize[BlueprintOptions]] = FileDeserialize()


def extend_data_pack(ctx: Context):
    ctx.data.extend_extra["myproject.json"] = JsonFile
    ctx.data.extend_namespace.append(FunctionConfig)
    ctx.data.extend_namespace.append(Blueprint)
    ctx.data.extend_namespace_extra["numbers.txt"] = TextFile


def process_functions(ctx: Context):
    project_data = cast(JsonFile, ctx.data.extra["myproject.json"]).data

    for prefix, dirs, functions in ctx.data.functions.walk():
        dirs.discard("zprivate")

        namespace = ctx.data[prefix.partition(":")[0]]
        numbers = cast(TextFile, namespace.extra["numbers.txt"]).text.splitlines()

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
