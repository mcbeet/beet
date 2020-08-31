__all__ = [
    "Pack",
    "PackOrigin",
    "Namespace",
    "FileContainerProxy",
    "FileContainer",
    "File",
    "JsonFile",
    "dump_data",
    "dump_copy",
    "dump_json",
]


import os
import json
import shutil
from contextlib import nullcontext
from dataclasses import dataclass, field, fields
from functools import partial
from pathlib import Path
from typing import (
    Any,
    Union,
    Optional,
    Generic,
    TypeVar,
    Type,
    Iterator,
    Dict,
    Tuple,
    Mapping,
    MutableMapping,
    get_args,
)
from zipfile import ZipFile

from .utils import FileSystemPath, ensure_optional_value


PackOrigin = Union[FileSystemPath, ZipFile]


def dump_data(data: bytes, dst: FileSystemPath, zipfile: ZipFile = None):
    if zipfile:
        zipfile.writestr(str(dst), data)
    else:
        Path(dst).write_bytes(data)


def dump_copy(src: FileSystemPath, dst: FileSystemPath, zipfile: ZipFile = None):
    if zipfile:
        zipfile.write(src, dst)
    else:
        shutil.copyfile(src, str(dst))


def dump_json(data: Any, dst: FileSystemPath, zipfile: ZipFile = None):
    dump_data((json.dumps(data, indent=2) + "\n").encode(), dst, zipfile)


@dataclass
class File:
    content: Optional[str] = None
    source_path: Optional[FileSystemPath] = None

    PATH = []
    EXTENSION = ""

    def bind(self, namespace: Any, path: str):
        pass

    def dump(self, path: FileSystemPath, zipfile: ZipFile = None):
        if self.source_path:
            dump_copy(self.source_path, path, zipfile)
        elif self.content is not None:
            dump_data(self.content.encode(), path, zipfile)


@dataclass
class JsonFile(File):
    content: Optional[dict] = None

    EXTENSION = ".json"

    def dump(self, path: FileSystemPath, zipfile: ZipFile = None):
        if self.content is not None:
            dump_json(self.content, path, zipfile)
        else:
            super().dump(path, zipfile)


FileType = TypeVar("FileType", bound=File)


class FileContainer(Dict[str, FileType]):
    __slots__ = ("namespace",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.namespace = None

    def __setitem__(self, path: str, item: FileType):
        super().__setitem__(path, item)
        if self.namespace:
            item.bind(self.namespace, path)

    def update(self, mapping: Mapping[str, FileType]):
        for path, item in mapping.items():
            self[path] = item

    def bind(self, namespace: Any):
        self.namespace = namespace
        for path, item in self.items():
            item.bind(namespace, path)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {super().__repr__()}>"

    @classmethod
    def field(cls) -> Any:
        return field(default_factory=cls)


class FileContainerProxy(MutableMapping[str, FileType]):
    __slots__ = ("pack", "container_name")

    def __init__(self, pack: Any, container_name: str):
        self.pack = pack
        self.container_name = container_name

    def __getitem__(self, key: str) -> FileType:
        container, path = self._preform_lookup(key)
        return container[path]

    def __setitem__(self, key: str, value: FileType):
        container, path = self._preform_lookup(key)
        container[path] = value

    def __delitem__(self, key: str):
        container, path = self._preform_lookup(key)
        del container[path]

    def __iter__(self) -> Iterator[str]:
        for namespace_name, namespace in self.pack.items():
            for path in getattr(namespace, self.container_name):
                yield f"{namespace_name}:{path}"

    def __len__(self):
        count = 0
        for namespace in self.pack.values():
            count += len(getattr(namespace, self.container_name))
        return count

    def _preform_lookup(self, key: str) -> Tuple[FileContainer[FileType], str]:
        namespace, _, item_path = key.partition(":")
        if not item_path:
            raise KeyError(key)
        return getattr(self.pack[namespace], self.container_name), item_path

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {dict(self)!r}>"

    @dataclass
    class Descriptor(Generic[FileType]):
        file_type: Type[FileType]
        name: Optional[str] = None

        def __set_name__(self, owner: Type[Any], name: str):
            self.name = name
            owner._proxy_registry = getattr(owner, "_proxy_registry", {})
            owner._proxy_registry[self.file_type] = name

        def __get__(self, instance: Any, owner=None) -> "FileContainerProxy[FileType]":
            if owner is None:
                raise AttributeError(self.name)
            return FileContainerProxy(instance, ensure_optional_value(self.name))

    @classmethod
    def field(cls, file_type: Type[FileType]) -> Descriptor[FileType]:
        return cls.Descriptor[FileType](file_type)


@dataclass
class Namespace:
    DIRECTORY = None

    def __post_init__(self):
        self.pack = None
        self.name = None
        self.contents: Dict[Type[File], FileContainer] = {
            get_args(field.type)[0]: getattr(self, field.name) for field in fields(self)
        }

    def bind(self, pack: Any, name: str):
        self.pack = pack
        self.name = name

        for container in self.contents.values():
            container.bind(self)

    def dump(self, namespace: str, pack: PackOrigin):
        for content_type, container in self.contents.items():
            if not container:
                continue

            path = [self.DIRECTORY, namespace] + content_type.PATH

            for name, item in container.items():
                full_path = path + [name + content_type.EXTENSION]

                if isinstance(pack, ZipFile):
                    item.dump("/".join(full_path), pack)
                else:
                    filename = Path(pack, *full_path).absolute()
                    filename.parent.mkdir(parents=True, exist_ok=True)
                    item.dump(filename)

    def __bool__(self) -> bool:
        return any(self.contents.values())


NamespaceType = TypeVar("NamespaceType", bound=Namespace)


@dataclass
class Pack(Dict[str, NamespaceType]):
    name: str
    description: Union[str, list, dict] = ""
    pack_format: int = 0

    zipped: bool = field(default=False)

    LATEST_PACK_FORMAT = -1

    def __post_init__(self):
        if not self.pack_format:
            self.pack_format = self.LATEST_PACK_FORMAT

    def __missing__(self, name: str) -> NamespaceType:
        namespace_type = get_args(getattr(self, "__orig_bases__")[0])[0]
        namespace = namespace_type()
        self[name] = namespace
        return namespace

    def __setitem__(self, key: str, item: Union[NamespaceType, File]):
        if isinstance(item, Namespace):
            super().__setitem__(key, item)
            item.bind(self, key)
        else:
            proxy_name = getattr(self, "_proxy_registry", {})[type(item)]
            getattr(self, proxy_name)[key] = item

    def update(self, mapping: Mapping[str, NamespaceType]):
        for key, item in mapping.items():
            self[key] = item

    @property
    def mcmeta(self):
        return {
            "pack": {
                "pack_format": self.pack_format,
                "description": self.description,
            }
        }

    def dump(
        self,
        directory: FileSystemPath,
        *,
        zipped: bool = None,
        overwrite: bool = False,
    ) -> Path:
        path = Path(directory).absolute()

        if zipped is None:
            zipped = self.zipped

        if zipped:
            output_path = path / f"{self.name}.zip"
            pack_factory = partial(ZipFile, mode="w")
        else:
            output_path = path / self.name
            pack_factory = nullcontext

        if output_path.exists():
            if overwrite:
                if output_path.is_dir():
                    shutil.rmtree(output_path)
                else:
                    os.remove(output_path)
            else:
                raise ValueError(f"Couldn't overwrite {str(output_path)!r}.")

        with pack_factory(output_path) as pack:
            if isinstance(pack, ZipFile):
                dump_json(self.mcmeta, "pack.mcmeta", pack)
            else:
                pack.mkdir(parents=True)
                dump_json(self.mcmeta, pack / "pack.mcmeta")

            for namespace_name, namespace in self.items():
                namespace.dump(namespace_name, pack)

        return output_path

    def __bool__(self) -> bool:
        return any(self.values())
