"""
Pack format registry resource from https://raw.githubusercontent.com/misode/mcmeta/refs/heads/summary/versions/data.json

see file://./../../scripts/update_pack_format_registry.py

"""

__all__ = [
    "pack_format_registry",
    "data_pack_format_registry",
    "resource_pack_format_registry",
    "pack_format_registry_path",
    "PackFormatRegistryContainer",
    "PackFormatRegistry",
]
from importlib.resources import files
import json
from typing import Mapping, Tuple
from pydantic import BaseModel
from beet.core.utils import normalize_string, VersionNumber
from beet.core.container import Container


class PackFormatRegistry(BaseModel):
    id: str
    name: str
    release_target: str | None
    type: str
    stable: bool
    data_version: int
    protocol_version: int
    data_pack_version: int
    resource_pack_version: int
    build_time: str
    release_time: str
    sha1: str


class PackFormatRegistryContainer(Container[VersionNumber, int]):
    """Container for pack format registry data."""

    def __init__(self, data: Mapping[VersionNumber, int]):
        super().__init__()
        for key, value in data.items():
            self[key] = value

    def normalize_key(self, key: VersionNumber) -> tuple[str | int, ...]:
        """Normalize the key to a tuple of integers."""
        if isinstance(key, (int, float)):
            key = str(key)
        if isinstance(key, str):
            key = tuple(normalize_string(key).split("_"))
        return tuple(int(value) if value != "x" else "x" for value in key)

    def missing(self, key: tuple[str | int, ...]) -> int:
        """
        Implement the missing method to return a default value.
        """
        if key[-1] == "x":
            max_patch = 0
            for version in self.keys():
                normalized_version = self.normalize_key(version)
                if key[0] != normalized_version[0] or key[1] != normalized_version[1]:
                    continue
                if len(normalized_version) == 2:
                    # The maximum is 0
                    continue
                patch = normalized_version[2]
                if isinstance(patch, int) and patch > max_patch:
                    max_patch = patch
            if max_patch == 0:
                return self[key[0], key[1]]
            return self[key[0], key[1], max_patch]
        raise KeyError(key)


pack_format_registry_path = files("beet.resources").joinpath(
    f"pack_format_registry.json"
)

data = json.loads(pack_format_registry_path.read_text())
pack_format_registry: list[PackFormatRegistry] = []
for item in data:
    pack_format_registry.append(PackFormatRegistry.model_validate(item))


data_pack_format_registry = PackFormatRegistryContainer(
    {x.id: x.data_pack_version for x in pack_format_registry if x.type == "release"}
)
resource_pack_format_registry = PackFormatRegistryContainer(
    {x.id: x.resource_pack_version for x in pack_format_registry if x.type == "release"}
)
