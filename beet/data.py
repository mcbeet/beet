__all__ = ["DataPack", "DataPackNamespace"]


from dataclasses import dataclass

from .common import Namespace, Pack


@dataclass
class DataPackNamespace(Namespace):
    pass


@dataclass
class DataPack(Pack[DataPackNamespace]):
    LATEST_PACK_FORMAT = 6
