"""
Pack format registry resource from https://raw.githubusercontent.com/misode/mcmeta/refs/heads/summary/versions/data.json

see file://./../../scripts/update_pack_format_registry.py

"""

__all__ = [
    "PackFormatRegistry",
    "PackFormatRegistryContainer",
    "pack_format_registry",
    "pack_format_registry_path",
]
import json
from importlib.resources import files
from typing import Literal

from pydantic import BaseModel

from beet.core.container import Container
from beet.core.utils import VersionNumber, normalize_version, resolve_version
from beet.toolchain.config import FormatSpecifier


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
for item in data:
    pack_format_registry.append(PackFormatRegistry.model_validate(item))


class PackFormatRegistryContainer(Container[VersionNumber, FormatSpecifier]):
    """Container for pack format registry data."""

    def __init__(
        self,
        pack_format_switch_format: int,
        pack_type: Literal["data_pack", "resource_pack"],
    ):
        super().__init__()
        if pack_type == "resource_pack":
            data: dict[VersionNumber, FormatSpecifier] = {
                (1, 6): 1,
                (1, 7): 1,
                (1, 8): 1,
                (1, 9): 2,
                (1, 10): 2,
                (1, 11): 3,
                (1, 12): 3,
                (1, 13): 4,
                **{
                    x.id: (
                        x.resource_pack_version
                        if x.resource_pack_version < pack_format_switch_format
                        else (x.resource_pack_version, x.resource_pack_version_minor)
                    )
                    for x in pack_format_registry
                    if x.type == "release"
                },
            }
        elif pack_type == "data_pack":
            data: dict[VersionNumber, FormatSpecifier] = {
                (1, 13): 4,
                **{
                    x.id: (
                        x.data_pack_version
                        if x.data_pack_version < pack_format_switch_format
                        else (x.data_pack_version, x.data_pack_version_minor)
                    )
                    for x in pack_format_registry
                    if x.type == "release"
                },
            }
        else:
            raise ValueError(
                f'Illegal "{pack_type}", should be "data_pack" or "resource_pack"'
            )
        for key, value in data.items():
            self[key] = value

    def normalize_key(self, key: VersionNumber) -> tuple[str | int, ...]:
        """Normalize the key to a tuple of integers."""
        return normalize_version(key)

    def missing(self, key: VersionNumber) -> FormatSpecifier:
        """
        Implement the missing method to return a default value.
        """
        version = resolve_version(key, self.keys())
        if version is None:
            raise KeyError(key)
        return self[version]
