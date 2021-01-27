__all__ = [
    "Mecha",
]


from dataclasses import InitVar, dataclass, field
from typing import Optional, Union

from beet import Context, DataPack


@dataclass
class Mecha:
    """Class exposing the command api."""

    target: InitVar[Union[Context, DataPack]]

    default_namespace: Optional[str] = None
    default_path: Optional[str] = None

    data_pack: DataPack = field(init=False)

    def __post_init__(self, target: Union[Context, DataPack]):
        if isinstance(target, Context):
            self.data_pack = target.data
            config = target.meta.get("mecha", {})
            default_namespace = config.get("default_namespace", target.project_name)
            default_path = config.get("default_path", "")
        else:
            self.data_pack = target
            default_namespace = self.data_pack.name or ""
            default_path = ""

        if self.default_namespace is None:
            self.default_namespace = default_namespace

        if self.default_path is None:
            self.default_path = default_path

    def resolve_path(self, path: str) -> str:
        """Resolve partial path."""
        namespace, sep, path = path.rpartition(":")

        if not namespace:
            namespace = self.default_namespace
        if not sep:
            path = f"{self.default_path}/{path}"

        return f"{namespace}:{path.strip('/')}".replace("//", "/").lower()
