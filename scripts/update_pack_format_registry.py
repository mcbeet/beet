import json
from typing import Any
from beet.resources.pack_format_registry import PackFormatRegistry, pack_format_registry_path
import requests

URL = "https://raw.githubusercontent.com/misode/mcmeta/refs/heads/summary/versions/data.json"

r = requests.get(URL)
r.raise_for_status()


pack_format_registry: list[dict[str, Any]] = []
for item in r.json():
    value = PackFormatRegistry.model_validate(item)
    if value.type == "release":
        pack_format_registry.append(value.model_dump())


with open(str(pack_format_registry_path), "w") as f:
    json.dump(pack_format_registry, f, indent=2)
    

