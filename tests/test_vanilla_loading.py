from pathlib import Path
from zipfile import ZipFile

from pydantic import BaseModel

from beet import Cache, DataPack, ResourcePack
from beet.contrib.unknown_files import UnknownAsset, UnknownData
from beet.contrib.vanilla import Vanilla
from beet.contrib.worldgen import worldgen
from beet.library.base import get_output_scope


class DatapackRegistryProperties(BaseModel):
    """Propriétés d'un registre ou élément"""

    elements: bool
    format: str | None = None
    stable: bool
    tags: bool


class DatapackOthers(BaseModel):
    """Section 'others' du fichier"""

    function: DatapackRegistryProperties
    structure: DatapackRegistryProperties


class DatapackRegistries(BaseModel):
    """Modèle racine pour le fichier de configuration Minecraft"""

    others: DatapackOthers
    registries: dict[str, DatapackRegistryProperties]


def resolve_key(key: str):
    return key if ":" in key else f"minecraft:{key}"


def get_scopes(dp: DataPack):
    all_scopes: dict[str, bool] = {}
    for file_type in dp.get_file_types():
        scope = get_output_scope(file_type.scope, dp)
        is_tags = scope[0] == "tags"
        if is_tags:
            scope = scope[1:]
        path = resolve_key("/".join(scope))
        all_scopes[path] = is_tags
    return all_scopes


def test_vanilla_loading(tmp_path: Path):
    vanilla = Vanilla(cache=Cache(tmp_path)).shared
    client = vanilla.client_jar.path

    dp = DataPack()
    rp = ResourcePack()
    dp.extend_namespace.append(UnknownData)
    rp.extend_namespace.append(UnknownAsset)

    worldgen(dp)
    dp.load(ZipFile(client))
    rp.load(ZipFile(client))

    dp_unknown = set()
    for key in dp[UnknownData]:
        splitted = key.split(":", 1)[1].split("/")
        if splitted[0] == "worldgen":
            dp_unknown.add("/".join(splitted[:2]))
        elif splitted[0] == "tags":
            if splitted[1] == "worldgen":
                dp_unknown.add("/".join(splitted[:3]))
            else:
                dp_unknown.add("/".join(splitted[:2]))
        else:
            dp_unknown.add(splitted[0])

    dp_unknown.remove("datapacks")

    rp_unknown = set()
    for key in rp[UnknownAsset]:
        splitted = key.split(":", 1)[1].split("/")
        if splitted[0] == "worldgen":
            rp_unknown.add("/".join(splitted[:2]))
        elif splitted[0] == "tags":
            if splitted[1] == "worldgen":
                rp_unknown.add("/".join(splitted[:3]))
            else:
                rp_unknown.add("/".join(splitted[:2]))
        else:
            rp_unknown.add(splitted[0])
    rp_unknown.remove("gpu_warnlist.json")
    rp_unknown.remove("regional_compliancies.json")

    assert len(dp_unknown) == 0, dp_unknown
    assert len(rp_unknown) == 0, rp_unknown


def test_registries(tmp_path: Path):
    vanilla = Vanilla(cache=Cache(tmp_path)).shared

    reports = vanilla.reports.mount("datapack.json")
    data_registries = DatapackRegistries.model_validate(reports["datapack"].data)

    dp_stable = DataPack()
    dp_unstable = DataPack()
    worldgen(dp_unstable)
    scope_stable = get_scopes(dp_stable)
    scope_unstable = get_scopes(dp_unstable)

    not_parsed_registries_stable = set()
    not_parsed_registries_unstable = set()
    not_parsed_registries_stable_tags = set()
    not_parsed_registries_unstable_tags = set()

    for key, value in data_registries.registries.items():
        key = resolve_key(key)
        if not value.elements:
            continue
        if value.stable:
            not_parsed_registries = not_parsed_registries_stable
            not_parsed_registries_tags = not_parsed_registries_stable_tags
            scope = scope_stable
        else:
            not_parsed_registries = not_parsed_registries_unstable
            not_parsed_registries_tags = not_parsed_registries_unstable_tags
            scope = scope_unstable
        if key not in scope:
            not_parsed_registries.add(key)
            continue
        if value.tags and not scope[key]:
            not_parsed_registries_tags.add(key)
    not_parsed_registries_stable = sorted(not_parsed_registries_stable)
    not_parsed_registries_unstable = sorted(not_parsed_registries_unstable)
    not_parsed_registries_stable_tags = sorted(not_parsed_registries_stable_tags)
    not_parsed_registries_unstable_tags = sorted(not_parsed_registries_unstable_tags)

    assert len(not_parsed_registries_stable) == 0, not_parsed_registries_stable
    assert len(not_parsed_registries_unstable) == 0, not_parsed_registries_unstable
    assert len(not_parsed_registries_stable_tags) == 0, (
        not_parsed_registries_stable_tags
    )
    assert len(not_parsed_registries_unstable_tags) == 0, (
        not_parsed_registries_unstable_tags
    )
