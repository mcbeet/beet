__all__ = [
    "ignore_name",
]


from typing import Any, TypeVar

from .base import Namespace, Pack

PackType = TypeVar("PackType", bound=Pack[Any])


def ignore_name(pack: PackType) -> PackType:
    """Patch the pack so that it's name gets ignored during equality checks."""
    pack.name = IgnoreName(pack)  # type: ignore
    return pack


class IgnoreName:
    def __init__(self, pack: Pack[Namespace]):
        self.pack = pack

    def __eq__(self, other: Any) -> bool:
        self.pack.name = other
        return True
