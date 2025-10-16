#!
import json
from typing import Any
import requests
from importlib.resources import files
from beet.resources.pack_format_registry import pack_format_registry_path

URL = "https://raw.githubusercontent.com/misode/mcmeta/refs/heads/summary/versions/data.json"

r = requests.get(URL)
r.raise_for_status()


pack_format_registry: list[dict[str, Any]] = []
for item in r.json():
    if item["type"] == "release":
        pack_format_registry.append(item)


with open(str(pack_format_registry_path), "w") as f:
    json.dump(pack_format_registry, f, indent=2)
