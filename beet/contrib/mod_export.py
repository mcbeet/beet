from typing import Dict, List
from zipfile import ZipFile

from beet import Context, JsonFile, PackFile, PluginOptions, TomlFile, configurable


class ModExportOptions(PluginOptions):
    fabric: bool = True
    quilt: bool = False
    neoforge: bool = True
    mcforge: bool = False

    # Human readable name of the datapack
    name: str | None = None
    # License of the datapack, or list of licenses. Recommended to use SPDX Licence identifiers, see https://spdx.org/licenses/
    license: str | List[str] | None = None
    # Object of contct information, keys typically include 'email', 'irc', 'homepage', 'issues', 'sources', but can contain others.
    # 'issues' and 'homepage' are used in forge, the entire object in fabric and quilt
    contact: Dict[str, str] | None = None
    # Override to minecraft version set in beet, to specify min and max
    min_minecraft_version: str | None = None
    max_minecraft_version: str | None = None
    # Override to auther set in beet. Use if you want to specify multiple authors
    authors: List[str] | None = None
    # Used to specify additional contributors that are not authors
    contributors: List[str] | None = None
    # Maven group. Required if quilt is enabled. Reccomended to follow java package name rules, i.e. a reversed domain name. Example: `dev.mcbeet`
    group: str | None = None


def beet_default(ctx: Context):
    ctx.require(mod_export)


@configurable(validator=ModExportOptions)
def mod_export(ctx: Context, opts: ModExportOptions):
    extra: Dict[str, PackFile] = dict()

    if opts.fabric:
        fabric(extra, ctx, opts)
    if opts.quilt:
        quilt(extra, ctx, opts)
    if opts.neoforge:
        forge(extra, ctx, opts, True)
    if opts.mcforge:
        forge(extra, ctx, opts, False)

    filename_template = (
        opts.name
        if opts.name is not None
        else (
            "{{project_id}}_{{project_version}}_mod"
            if ctx.project_version != ""
            else "{{project_id}}_mod"
        )
    )

    if ctx.output_directory is None:
        raise RuntimeError("no output directory set")

    ctx.output_directory.mkdir(parents=True, exist_ok=True)
    with ZipFile(
        f"{ctx.output_directory}/{ctx.template.render_string(filename_template)}.jar",
        mode="w",
    ) as z:
        ctx.assets.dump(z)
        ctx.data.dump(z)
        for path, item in extra.items():
            item.dump(z, path)


def fabric(extra: Dict[str, PackFile], ctx: Context, opts: ModExportOptions):
    minecraft_version_string = (
        f">={opts.min_minecraft_version} <{opts.max_minecraft_version}"
        if opts.min_minecraft_version is not None
        and opts.max_minecraft_version is not None
        else ctx.minecraft_version
    )

    config = {
        "schemaVersion": 1,
        "id": ctx.project_id,
        "version": ctx.project_version,
        "name": ctx.project_name,
        "description": ctx.project_description,
        "license": opts.license,
        "authors": opts.authors if opts.authors is not None else [ctx.project_author],
        "contributors": opts.contributors,
        "contact": opts.contact,
        "icon": "pack.png",
        "depends": {
            "fabricloader": ">=0.12.7",
            "fabric-resource-loader-v0": "*",
            "minecraft": minecraft_version_string,
        },
    }

    extra["fabric.mod.json"] = JsonFile(
        {k: v for (k, v) in config.items() if v is not None}
    )


def quilt(extra: Dict[str, PackFile], ctx: Context, opts: ModExportOptions):
    minecraft_version_string = (
        {"all": [f">={opts.min_minecraft_version}", f"<{opts.max_minecraft_version}"]}
        if opts.min_minecraft_version is not None
        and opts.max_minecraft_version is not None
        else ctx.minecraft_version
    )

    assert opts.group is not None

    metadata = {
        "name": ctx.project_name,
        "description": ctx.project_description,
        "contributors": {
            **{
                a: "Author"
                for a in (
                    opts.authors if opts.authors is not None else [ctx.project_author]
                )
            },
            **{
                a: "Contributor"
                for a in (opts.contributors if opts.contributors is not None else [])
            },
        },
        "contact": opts.contact,
        "license": opts.license,
        "icon": "pack.png",
    }

    extra["quilt.mod.json"] = JsonFile(
        {
            "schema_version": 1,
            "quilt_loader": {
                "group": opts.group,
                "id": ctx.project_id,
                "version": ctx.project_version,
                "metadata": {k: v for (k, v) in metadata.items() if v is not None},
                "intermediate_mappings": "net.fabricmc:intermediary",
                "depends": [
                    {"id": "minecraft", "versions": minecraft_version_string},
                    {
                        "id": "quilt_resource_loader",
                        "versions": "*",
                        "unless": "fabric-resource-loader-v0",
                    },
                ],
            },
        }
    )


def forge(
    extra: Dict[str, PackFile], ctx: Context, opts: ModExportOptions, isNeo: bool
):
    minecraft_version_string = (
        f"[{opts.min_minecraft_version},{opts.max_minecraft_version})"
        if opts.min_minecraft_version is not None
        and opts.max_minecraft_version is not None
        else ctx.minecraft_version
    )

    extra["META-INF/neoforge.mods.toml" if isNeo else "META-INF/mods.toml"] = TomlFile(
        {
            "modLoader": "lowcodefml",
            "loaderVersion": "[1,)",
            "license": opts.license,
            "issueTrackerURL": (
                opts.contact["issues"]
                if opts.contact is not None and "issues" in opts.contact
                else None
            ),
            "mods": [
                {
                    "modId": ctx.project_id,
                    "version": ctx.project_version,
                    "displayName": ctx.project_name,
                    "description": ctx.project_description,
                    "logoFile": "pack.png",
                    "authors": ", ".join(
                        opts.authors
                        if opts.authors is not None
                        else [ctx.project_author]
                    ),
                    "credits": (
                        ("Contributors: " + ", ".join(opts.contributors))
                        if opts.contributors is not None
                        else None
                    ),
                    "displayURL": (
                        opts.contact["homepage"]
                        if opts.contact is not None and "homepage" in opts.contact
                        else None
                    ),
                }
            ],
            "dependencies": {
                ctx.project_id: [
                    {
                        "modId": "neoforge" if isNeo else "forge",
                        "mandatory": None if isNeo else False,
                    },
                    {
                        "modId": "minecraft",
                        "mandatory": None if isNeo else True,
                        "versionRange": minecraft_version_string,
                    },
                ]
            },
        }
    )
