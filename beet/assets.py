__all__ = ["ResourcePack", "ResourcePackNamespace"]


from dataclasses import dataclass

from .common import Namespace, Pack


@dataclass
class ResourcePackNamespace(Namespace):
    pass


@dataclass
class ResourcePack(Pack[ResourcePackNamespace]):
    latest_pack_format = 6
