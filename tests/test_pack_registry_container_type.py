from beet.library.data_pack import DataPack
import json
import requests
from beet.resources.pack_format_registry import (
    pack_format_registry_path,
    PackFormatRegistry,
)


def test_registry_data():
    assert DataPack.pack_format_registry.normalize_key("1.21") == (1, 21)
    assert DataPack.pack_format_registry.normalize_key("1.21.1") == (1, 21, 1)
    assert DataPack.pack_format_registry.normalize_key("1.21.x") == (1, 21, "x")

    assert DataPack.pack_format_registry.missing((1, 20, "x")) == 41
    assert DataPack.pack_format_registry.missing((1, 19, "x")) == 12

    assert DataPack.pack_format_registry.get((1, 21, 10)) == (88, 0)
    assert DataPack.pack_format_registry.get((1, 21, 9)) == (88, 0)

    assert DataPack.pack_format_registry.get((1, 20)) == 15
    assert DataPack.pack_format_registry.get((1, 18)) == 8


def redact_sha1(x: PackFormatRegistry) -> PackFormatRegistry:
    x.sha1 = ""
    return x


def test_misode_mcmeta():
    URL = "https://raw.githubusercontent.com/misode/mcmeta/refs/heads/summary/versions/data.json"
    r = requests.get(URL)
    r.raise_for_status()
    misode_data = [redact_sha1(PackFormatRegistry.model_validate(x)) for x in r.json()]
    misode_data = [x for x in misode_data if x.type == "release"]

    with open(str(pack_format_registry_path), "r") as f:
        beet_data = json.load(f)
    beet_data = [redact_sha1(PackFormatRegistry.model_validate(x)) for x in beet_data]
    for x in misode_data:
        assert x in beet_data
    for x in beet_data:
        assert x in misode_data
