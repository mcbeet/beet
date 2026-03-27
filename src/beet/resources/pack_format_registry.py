"""
Pack format registry resource from https://raw.githubusercontent.com/misode/mcmeta/refs/heads/summary/versions/data.json

see file://./../../../scripts/update_pack_format_registry.py

"""

__all__ = [
    "pack_format_registry",
    "pack_format_registry_path",
    "PackFormatRegistryContainer",
    "PackFormatRegistry",
    "search_version",
]
from importlib.resources import files
import json
from typing import Literal

from beet.toolchain.config import FormatSpecifier
from pydantic import BaseModel
from beet.core.utils import VersionNumber
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
    data_pack_version_minor: int
    resource_pack_version: int
    resource_pack_version_minor: int


pack_format_registry_path = files("beet.resources").joinpath(
    "pack_format_registry.json"
)

data = json.loads(pack_format_registry_path.read_text())
pack_format_registry: list[PackFormatRegistry] = []
all_versions: list[str] = []
for item in data:
    pack_format = PackFormatRegistry.model_validate(item)
    all_versions.append(pack_format.id)
    pack_format_registry.append(pack_format)


def search_version(version: VersionNumber) -> str:
    """
    This function search a version specifier and return a version
    """
    if isinstance(version, tuple):
        version = ".".join(str(x) for x in version)
    if isinstance(version, str) and version in all_versions:
        return version
    if isinstance(version, str) and version.endswith(".x"):
        major, minor, _ = version.split(".", 2)
        max_patch = 0
        for search in all_versions:
            search_splitted = search.split(".")
            if search_splitted[0] != major or search_splitted[1] != minor:
                continue
            if len(search_splitted) == 3:
                search_patch = int(search_splitted[2])
                if search_patch > max_patch:
                    max_patch = search_patch

        if max_patch == 0:
            return f"{major}.{minor}"
        else:
            return f"{major}.{minor}.{max_patch}"
    raise KeyError(version)


class PackFormatRegistryContainer(Container[VersionNumber, FormatSpecifier]):
    """Container for pack format registry data."""

    pack_format_switch_format: int
    pack_type: Literal["data_pack", "resource_pack"]

    def __init__(
        self,
        pack_format_switch_format: int,
        pack_type: Literal["data_pack", "resource_pack"],
    ):
        self.pack_format_switch_format = pack_format_switch_format
        self.pack_type = pack_type
        super().__init__()
        default_data: dict[VersionNumber, FormatSpecifier]
        if pack_type == "resource_pack":
            default_data = {
                (1, 6): 1,
                (1, 7): 1,
                (1, 8): 1,
                (1, 9): 2,
                (1, 10): 2,
                (1, 11): 3,
                (1, 12): 3,
                (1, 13): 4,
            }
        elif pack_type == "data_pack":
            default_data = {
                (1, 13): 4,
            }
        else:
            raise ValueError(
                f'Illegal "{pack_type}", should be "data_pack" or "resource_pack"'
            )
        for key, value in default_data.items():
            self[key] = value

        for version in pack_format_registry:
            self.add_format(version)

    def add_format(self, version: PackFormatRegistry):
        if self.pack_type == "data_pack":
            self[version.id] = (
                version.data_pack_version
                if version.data_pack_version < self.pack_format_switch_format
                else (version.data_pack_version, version.data_pack_version_minor)
            )
        elif self.pack_type == "resource_pack":
            self[version.id] = (
                version.resource_pack_version
                if version.resource_pack_version < self.pack_format_switch_format
                else (
                    version.resource_pack_version,
                    version.resource_pack_version_minor,
                )
            )

    def normalize_key(self, key: VersionNumber) -> str:
        """Normalize the key to a string."""
        if isinstance(key, str):
            return key
        if isinstance(key, (int, float)):
            return str(key)
        if isinstance(key, tuple):
            return ".".join(str(x) for x in key)
        raise NotImplementedError()

    def missing(self, key: VersionNumber) -> FormatSpecifier:
        """
        Implement the missing method to return a default value.
        """
        version = search_version(key)
        res = self.get(version)
        if res:
            return res
        raise KeyError(key)
