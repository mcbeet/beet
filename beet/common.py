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
    "load_data",
    "load_json",
    "open_fileobj",
]


import os
import json
import shutil
from contextlib import nullcontext
from dataclasses import dataclass, field
from functools import partial
from itertools import accumulate
from pathlib import Path
from typing import (
    Any,
    Union,
    Optional,
    Generic,
    TypeVar,
    ClassVar,
    Type,
    Iterator,
    Dict,
    ItemsView,
    Tuple,
    Mapping,
    MutableMapping,
    IO,
    get_type_hints,
    get_origin,
    get_args,
)
from zipfile import ZipFile

from .utils import FileSystemPath, ensure_optional_value, extra_field, list_files


PackOrigin = Union[FileSystemPath, ZipFile]

T = TypeVar("T")
NamespaceType = TypeVar("NamespaceType", bound="Namespace")
FileType = TypeVar("FileType", bound="File")


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


def load_data(src: FileSystemPath, zipfile: ZipFile = None) -> bytes:
    if zipfile:
        return zipfile.read(str(src))
    else:
        return Path(src).read_bytes()


def load_json(src: FileSystemPath, zipfile: ZipFile = None) -> Any:
    return json.loads(load_data(src, zipfile).decode())


def open_fileobj(path: FileSystemPath, mode: str, zipfile: ZipFile = None) -> IO:
    if zipfile:
        return zipfile.open(str(path), mode)
    else:
        return open(path, mode + "b")


@dataclass
class File:
    content: Optional[str] = None
    source_path: Optional[FileSystemPath] = None

    PATH: ClassVar[Tuple[str, ...]]
    EXTENSION: ClassVar[str]

    def bind(self, namespace: Any, path: str):
        pass

    @classmethod
    def load(
        cls: Type[FileType], path: FileSystemPath, zipfile: ZipFile = None
    ) -> FileType:
        return cls(load_data(path, zipfile).decode())

    def dump(self, path: FileSystemPath, zipfile: ZipFile = None):
        if self.source_path:
            dump_copy(self.source_path, path, zipfile)
        elif self.content is not None:
            dump_data(self.content.encode(), path, zipfile)


@dataclass
class JsonFile(File):
    content: Optional[dict] = None

    EXTENSION = ".json"

    @classmethod
    def load(
        cls: Type[FileType], path: FileSystemPath, zipfile: ZipFile = None
    ) -> FileType:
        return cls(load_json(path, zipfile))

    def dump(self, path: FileSystemPath, zipfile: ZipFile = None):
        if self.content is not None:
            dump_json(self.content, path, zipfile)
        else:
            super().dump(path, zipfile)


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
        return f"<{self.__class__.__name__}: {list(self.keys())}>"

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
        return f"<{self.__class__.__name__}: {list(self.keys())}>"

    @dataclass
    class Descriptor(Generic[FileType]):
        file_type: Type[FileType]
        name: Optional[str] = None

        def __set_name__(self, owner: Type[Any], name: str):
            self.name = name

        def __get__(self, instance: Any, owner=None) -> "FileContainerProxy[FileType]":
            if owner is None:
                raise AttributeError(self.name)
            return FileContainerProxy(instance, ensure_optional_value(self.name))

    @classmethod
    def field(cls, file_type: Type[FileType]) -> Descriptor[FileType]:
        return cls.Descriptor[FileType](file_type)


@dataclass
class Namespace(Dict[Type[File], FileContainer]):
    pack: Optional[Any] = extra_field(default=None, init=False)
    name: Optional[str] = extra_field(default=None, init=False)

    DIRECTORY: ClassVar[str]
    PATH_MAPPING: ClassVar[Dict[Tuple[Tuple[str, ...], str], Type[File]]]
    CONTAINER_FIELDS: ClassVar[Dict[Type[File], str]]

    def __init_subclass__(cls: Type["Namespace"]):
        cls.CONTAINER_FIELDS = {
            get_args(hint)[0]: attr
            for attr, hint in get_type_hints(cls).items()
            if get_origin(hint) is FileContainer
        }
        cls.PATH_MAPPING = {
            (file_type.PATH, file_type.EXTENSION): file_type
            for file_type in cls.CONTAINER_FIELDS
        }

    def __post_init__(self):
        for file_type, attr in self.CONTAINER_FIELDS.items():
            super().__setitem__(file_type, getattr(self, attr))

    def __setitem__(self, key: str, item: File):
        self[type(item)][key] = item

    def update(self, mapping: Dict[str, File]):
        for key, item in mapping.items():
            self[key] = item

    def bind(self, pack: Any, name: str):
        self.pack = pack
        self.name = name

        for container in self.values():
            container.bind(self)

    @classmethod
    def load_from(cls: Type[T], pack: PackOrigin) -> Iterator[Tuple[str, T]]:
        if isinstance(pack, ZipFile):
            filenames = map(Path, pack.namelist())
        else:
            filenames = list_files(pack)

        name = None
        namespace = None

        for filename in sorted(filenames):
            try:
                directory, namespace_dir, head, *rest, basename = filename.parts
            except ValueError:
                continue

            if directory != cls.DIRECTORY:
                continue
            elif name != namespace_dir:
                name = namespace_dir
                namespace = cls()
                yield name, namespace

            name = ensure_optional_value(name)
            namespace = ensure_optional_value(namespace)
            extension = filename.suffix

            for path in accumulate(rest, lambda a, b: (*a, b), initial=(head,)):
                if file_type := cls.PATH_MAPPING.get((path, extension)):
                    prefix = Path(directory, name, *path)
                    key = "/".join(filename.relative_to(prefix).with_suffix("").parts)

                    namespace[file_type][key] = (
                        file_type.load(str(filename), pack)
                        if isinstance(pack, ZipFile)
                        else file_type.load(pack / filename)
                    )
                    break

    def dump(self, namespace: str, pack: PackOrigin):
        for content_type, container in self.items():
            if not container:
                continue

            path = (self.DIRECTORY, namespace) + content_type.PATH

            for name, item in container.items():
                full_path = path + (name + content_type.EXTENSION,)

                if isinstance(pack, ZipFile):
                    item.dump("/".join(full_path), pack)
                else:
                    filename = Path(pack, *full_path).absolute()
                    filename.parent.mkdir(parents=True, exist_ok=True)
                    item.dump(filename)

    def __ne__(self, obj: object) -> bool:
        return not (self == obj)

    def __bool__(self) -> bool:
        return any(self.values())


@dataclass
class Pack(Dict[str, NamespaceType]):
    name: Optional[str] = None
    description: Union[str, list, dict] = ""
    pack_format: int = 0

    namespaces: ItemsView[str, NamespaceType] = field(init=False, repr=False)
    zipped: Optional[bool] = extra_field(default=None)

    path: Optional[FileSystemPath] = extra_field(default=None)
    zipfile: Optional[ZipFile] = extra_field(default=None)

    NAMESPACE_TYPE: ClassVar[Type[NamespaceType]]
    LATEST_PACK_FORMAT: ClassVar[int]

    def __init_subclass__(cls: Type["Pack"]):
        cls.NAMESPACE_TYPE = get_args(getattr(cls, "__orig_bases__")[0])[0]

    def __post_init__(self):
        self.namespaces = self.items()
        self.load()

    def __missing__(self, name: str) -> NamespaceType:
        namespace = self.NAMESPACE_TYPE()
        self[name] = namespace
        return namespace

    def __setitem__(self, key: str, item: Union[NamespaceType, File]):
        if isinstance(item, Namespace):
            super().__setitem__(key, item)
            item.bind(self, key)
        else:
            attr = self.NAMESPACE_TYPE.CONTAINER_FIELDS[type(item)]
            getattr(self, attr)[key] = item

    def update(self, mapping: Mapping[str, NamespaceType]):
        for key, item in mapping.items():
            self[key] = item

    def get_mcmeta(self) -> dict:
        return {
            "pack": {
                "pack_format": self.pack_format,
                "description": self.description,
            }
        }

    def set_mcmeta(self, mcmeta: dict):
        pack = mcmeta.get("pack", {})

        if "pack_format" in pack:
            self.pack_format = pack["pack_format"]
        if "description" in pack:
            self.description = pack["description"]

    mcmeta = property(get_mcmeta, set_mcmeta)

    def __enter__(self: T) -> T:
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.dump(overwrite=True)

    def load(self, pack: PackOrigin = None):
        if pack is not None:
            if isinstance(pack, ZipFile):
                self.zipfile = pack
            elif not os.path.exists(pack):
                raise FileNotFoundError(pack)
            else:
                self.path = pack

        path = Path(self.path).absolute() if self.path else None

        if not self.name:
            self.name = (self.zipfile and self.zipfile.filename) or (path and path.stem)
        if self.zipped is None:
            self.zipped = bool(self.zipfile) or (path and path.suffix == ".zip")

        origin = self.zipfile

        if not origin and path:
            if path.is_file():
                origin = ZipFile(path)
            elif path.is_dir():
                origin = path

        if origin:
            if isinstance(origin, ZipFile):
                self.mcmeta = load_json("pack.mcmeta", origin)
            else:
                self.mcmeta = load_json(origin / "pack.mcmeta")

            for name, namespace in self.NAMESPACE_TYPE.load_from(origin):
                self[name] = namespace

        if not self.pack_format:
            self.pack_format = self.LATEST_PACK_FORMAT

    def dump(
        self,
        directory: FileSystemPath = None,
        *,
        zipped: bool = None,
        overwrite: bool = False,
    ) -> Path:
        if not directory:
            directory = Path(self.path).parent if self.path else Path.cwd()

        path = Path(directory).absolute()

        if zipped is None:
            zipped = bool(self.zipped)

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

    def __ne__(self, obj: object) -> bool:
        return not (self == obj)

    def __bool__(self) -> bool:
        return any(self.values())
