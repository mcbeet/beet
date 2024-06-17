from typing import ClassVar, Tuple, cast

from pydantic.v1 import BaseModel

from beet import Context, FileDeserialize, JsonFile, JsonFileBase, TextFile, YamlFile


class FunctionConfig(YamlFile):
    scope: ClassVar[list[Tuple[str, ...]]] = ("functions",)
    extension: ClassVar[str] = ".yml"


class BlueprintData(BaseModel):
    name: str


class Blueprint(JsonFileBase[BlueprintData]):
    model = BlueprintData

    scope: ClassVar[list[Tuple[str, ...]]] = ("blueprints",)
    extension: ClassVar[str] = ".json"

    data: ClassVar[FileDeserialize[BlueprintData]] = FileDeserialize()


def extend_data_pack(ctx: Context):
    ctx.data.extend_extra["myproject.json"] = JsonFile
    ctx.data.extend_namespace.append(FunctionConfig)
    ctx.data.extend_namespace.append(Blueprint)
    ctx.data.extend_namespace_extra["numbers.txt"] = TextFile


def process_functions(ctx: Context):
    project_data = cast(JsonFile, ctx.data.extra["myproject.json"]).data

    for prefix, dirs, functions in ctx.data.function.walk():
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
