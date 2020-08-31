__all__ = [
    "Pack",
    "PackOrigin",
    "Namespace",
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
from typing import Optional, TypeVar, Dict, Mapping, Type, Union, Any, get_args
from zipfile import ZipFile

from .utils import FileSystemPath


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

    def bind(self, namespace: Any):
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.namespace = None

    def __setitem__(self, key: str, item: FileType):
        super().__setitem__(key, item)

        if self.namespace:
            item.bind(self.namespace)

    def update(self, mapping: Mapping[str, FileType]):
        for key, item in mapping.items():
            self[key] = item

    def bind(self, namespace: Any):
        self.namespace = namespace

        for item in self.values():
            item.bind(namespace)

    @classmethod
    def field(cls):
        return field(default_factory=cls)


@dataclass
class Namespace:
    DIRECTORY = None

    def __post_init__(self):
        self.pack = None
        self.contents: Dict[Type[File], FileContainer] = {
            get_args(field.type)[0]: getattr(self, field.name) for field in fields(self)
        }

    def bind(self, pack: Any):
        self.pack = pack

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

    def __missing__(self, key) -> NamespaceType:
        namespace_type = get_args(getattr(self, "__orig_bases__")[0])[0]
        namespace = namespace_type()
        self[key] = namespace
        return namespace

    def __setitem__(self, key: str, item: NamespaceType):
        super().__setitem__(key, item)
        item.bind(self)

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

            for key, namespace in self.items():
                namespace.dump(key, pack)

        return output_path

    def __bool__(self) -> bool:
        return any(self.values())
