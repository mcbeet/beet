"""Plugin that implements Lantern Load runtime dependencies."""


from typing import cast

from beet import Context, Function, FunctionTag
from beet.core.utils import JsonDict


def beet_default(ctx: Context):
    # Add the necessary boilerplate to the data pack.
    # This could also be done by merging a base data pack embedded inside the package.
    ctx.require(base_data_pack)

    # Grab the Lantern Load configuration.
    # The id defaults to the project name and the version to the project version.
    config = ctx.meta.get("lantern_load", cast(JsonDict, {}))

    id = config.get("id", ctx.project_name)
    version = config.get("version", ctx.project_version)
    dependencies = config.get("dependencies", cast(JsonDict, {}))

    # Populate the #load:load tag with the dependencies followed by the pack's
    # own load function.
    load_tag_values = [
        *({"id": f"#{dep}:load", "required": False} for dep in dependencies),
        f"{id}:load",
    ]

    ctx.data.function_tags["load:load"].data["values"].append(f"#{id}:load")
    ctx.data[f"{id}:load"] = FunctionTag({"values": load_tag_values})

    # Generate and join version checks for all the dependencies.
    # Currently this only matches a major version number against a fixed value or a range.
    version_checks = " ".join(
        f"if score {dep}.major load.status matches {version}"
        for dep, version in dependencies.items()
    )

    prefix = f"execute {version_checks} run " if version_checks else ""

    # Implement the load function by first showing a message if there are any missing dependency
    # and then setting the pack's own version before calling the pack's init tag.
    ctx.data[f"{id}:load"] = Function(
        [
            *(
                f"execute unless score {dep}.major load.status matches {version} run say {id}: missing dependency {dep}=={version}"
                for dep, version in dependencies.items()
            ),
            f"{prefix}scoreboard players set {id}.major load.status {version}",
            f"execute if score {id}.major load.status matches {version} run function #{id}:init",
        ]
    )


def base_data_pack(ctx: Context):
    ctx.data["minecraft:load"] = FunctionTag({"values": ["#load:_private/load"]})
    ctx.data["load:_private/load"] = FunctionTag(
        {
            "values": [
                "#load:_private/init",
                {"id": "#load:pre_load", "required": False},
                {"id": "#load:load", "required": False},
                {"id": "#load:post_load", "required": False},
            ]
        }
    )

    ctx.data["load:_private/init"] = FunctionTag({"values": ["load:_private/init"]})
    ctx.data["load:_private/init"] = Function(
        [
            "scoreboard objectives add load.status dummy",
            "scoreboard players reset * load.status",
        ]
    )

    ctx.data.function_tags.merge(
        {
            "load:pre_load": FunctionTag(),
            "load:load": FunctionTag(),
            "load:post_load": FunctionTag(),
        }
    )
