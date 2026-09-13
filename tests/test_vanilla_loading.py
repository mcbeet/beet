from pathlib import Path

from beet import DataPack, ResourcePack, Cache, LATEST_MINECRAFT_VERSION, JsonFile
from beet.contrib.unknown_files import UnknownAsset, UnknownData
from beet.contrib.worldgen import worldgen
from beet.contrib.vanilla import MANIFEST_URL
from zipfile import ZipFile


def test_vanilla_loading(tmp_path: Path):
    cache = Cache(tmp_path)
    manifest = JsonFile(source_path=cache.download(MANIFEST_URL))
    version = [
        x for x in manifest.data["versions"] if x["id"] == LATEST_MINECRAFT_VERSION
    ][0]
    version_manifest = JsonFile(source_path=cache.download(version["url"]))
    client = cache.download(version_manifest.data["downloads"]["client"]["url"])

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
