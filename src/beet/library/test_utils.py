__all__ = [
    "ignore_name",
]


from typing import Any

from .base import Namespace, Pack


def ignore_name[PackType: Pack[Any]](pack: PackType) -> PackType:
    """Patch the pack so that it's name gets ignored during equality checks."""
    pack.name = IgnoreName(pack)  # pyright: ignore[reportAttributeAccessIssue]
    return pack


class IgnoreName:
    def __init__(self, pack: Pack[Namespace]):
        self.pack = pack

    def __eq__(self, other: object) -> bool:
        self.pack.name = other  # pyright: ignore[reportAttributeAccessIssue]
        return True
