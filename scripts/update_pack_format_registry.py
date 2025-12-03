#!
import json
from typing import Any
import requests
from beet.resources.pack_format_registry import pack_format_registry_path
from importlib.resources import files
from beet.core.utils import split_version

URL_VERSIONS = "https://raw.githubusercontent.com/misode/mcmeta/refs/heads/summary/versions/data.json"
URL_COMMAND_TREE = "https://raw.githubusercontent.com/misode/mcmeta/refs/tags/{version}-summary/commands/data.json"

r = requests.get(URL_VERSIONS)
r.raise_for_status()


pack_format_registry: list[dict[str, Any]] = []
for item in r.json():
    if item["type"] == "release":
        pack_format_registry.append(item)
        version_name = "_".join(map(str, split_version(item["id"])))
        try:
            r = requests.get(URL_COMMAND_TREE.format(version=item["id"]))
            r.raise_for_status()
            path = str(files("mecha.resources").joinpath(f"{version_name}.json"))

            with open(path, "w") as f:
                f.write(r.text)
        except BaseException as e:
            print(f"Failed to download command tree for version {version_name}.")
            print(f"Error: {e}")
            continue


with open(str(pack_format_registry_path), "w") as f:
    json.dump(pack_format_registry, f, indent=2)
