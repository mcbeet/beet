__all__ = ["Pack", "NamespaceContainer", "Namespace", "File", "JsonFile"]


from dataclasses import dataclass
from typing import Optional, TypeVar, DefaultDict, get_args

from .utils import FileSystemPath


@dataclass
class File:
    source_path: Optional[FileSystemPath] = None
    content: Optional[str] = None

    def __post_init__(self):
        if self.source_path is not None == self.content is not None:
            raise ValueError("You must specify either 'source_path' or 'content'")


@dataclass
class JsonFile(File):
    json: Optional[dict] = None

    def __post_init__(self):
        if self.json is None:
            super().__post_init__()
        elif self.source_path is not None or self.content is not None:
            raise ValueError(
                "You can't specify 'json' in combination with 'source_path' or 'content'"
            )


@dataclass
class Namespace:
    pass


NamespaceType = TypeVar("NamespaceType", bound=Namespace)


class NamespaceContainer(DefaultDict[str, NamespaceType]):
    def __new__(cls, *args, **kwargs):
        namespace_type = get_args(getattr(cls, "__orig_bases__")[0])[0]
        return super().__new__(cls, default_factory=namespace_type)

    def __bool__(self):
        return all(self.values())


@dataclass
class Pack(NamespaceContainer[NamespaceType]):
    name: str
    description: str = ""
    pack_format: int = 0

    LATEST_PACK_FORMAT = -1

    def __post_init__(self):
        if not self.pack_format:
            self.pack_format = self.LATEST_PACK_FORMAT
