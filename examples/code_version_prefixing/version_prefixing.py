from beet import Context
from beet.contrib.rename_files import rename_files
from beet.contrib.find_replace import find_replace
from beet.contrib.function_header import function_header


def beet_default(ctx: Context):
    ctx.require(
        rename_files(
            data_pack={
                "match": f"{ctx.project_id}:*",
                "find": rf"{ctx.project_id}:(?!no_prefix/)([a-z0-9_/]+)",
                "replace": rf"{ctx.project_id}:v{ctx.project_version}/\1",
            }
        ),
        find_replace(
            data_pack={"match": f"{ctx.project_id}:*"},
            substitute={
                "find": rf"{ctx.project_id}:(?!no_prefix/)([a-z0-9_/]+)",
                "replace": rf"{ctx.project_id}:v{ctx.project_version}/\1",
            },
        ),
        function_header(
            match=[rf"{ctx.project_id}:*", rf"!{ctx.project_id}:no_prefix/*"],
            template="version_check.mcfunction",
        ),
    )
