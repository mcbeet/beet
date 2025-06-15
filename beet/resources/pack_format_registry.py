"""
Pack format registry resource from https://raw.githubusercontent.com/misode/mcmeta/refs/heads/summary/versions/data.json
"""

__all__ = [
    "pack_format_registry",
    "data_pack_format_registry",
    "resource_pack_format_registry",
]
from importlib.resources import files
import json
from pydantic import BaseModel
from beet.core.utils import split_version


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


data = json.loads(
    files("beet.resources").joinpath(f"pack_format_registry.json").read_text()
)
pack_format_registry: list[PackFormatRegistry] = []
for item in data:
    pack_format_registry.append(PackFormatRegistry.model_validate(item))


data_pack_format_registry = {
    split_version(x.id): x.data_pack_version
    for x in pack_format_registry
    if x.type == "release"
}
resource_pack_format_registry = {
    split_version(x.id): x.resource_pack_version
    for x in pack_format_registry
    if x.type == "release"
}
