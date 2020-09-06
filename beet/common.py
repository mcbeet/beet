__all__ = [
    "Pack",
    "PackOrigin",
    "Namespace",
    "FileContainer",
    "FileContainerProxy",
    "FileContainerProxyDescriptor",
    "File",
    "JsonFile",
]


import os
import json
import shutil
from contextlib import nullcontext
from dataclasses import dataclass, field
from functools import partial
from itertools import accumulate
from pathlib import Path, PurePath
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
    get_type_hints,
    get_origin,
    get_args,
    cast,
)
from zipfile import ZipFile

from .utils import FileSystemPath, dump_json, extra_field, list_files


PackOrigin = Union[FileSystemPath, ZipFile]

T = TypeVar("T")
NamespaceType = TypeVar("NamespaceType", bound="Namespace")
FileType = TypeVar("FileType", bound="File")


@dataclass
class File(Generic[T]):
    raw: Optional[Union[T, bytes]] = None
    source_path: Optional[FileSystemPath] = None

    path: ClassVar[Tuple[str, ...]]
    extension: ClassVar[str]

    def to_content(self, raw: bytes) -> T:
        raise NotImplementedError()

    def to_bytes(self, content: T) -> bytes:
        raise NotImplementedError()

    @property
    def content(self) -> T:
        if self.raw is None:
            assert self.source_path
            self.raw = Path(self.source_path).read_bytes()
            self.source_path = None
        if isinstance(self.raw, bytes):
            self.raw = self.to_content(self.raw)
        return self.raw

    @content.setter
    def content(self, value: T):
        self.raw = value

    def bind(self, namespace: Any, path: str):
        pass

    @classmethod
    def load(
        cls: Type[FileType], path: FileSystemPath, zipfile: ZipFile = None
    ) -> FileType:
        return cls(zipfile.read(str(path))) if zipfile else cls(source_path=path)

    def dump(self, path: FileSystemPath, zipfile: ZipFile = None):
        if self.raw is None:
            assert self.source_path
            if zipfile:
                zipfile.write(self.source_path, str(path))
            else:
                shutil.copyfile(self.source_path, str(path))
        else:
            raw = self.raw if isinstance(self.raw, bytes) else self.to_bytes(self.raw)
            if zipfile:
                zipfile.writestr(str(path), raw)
            else:
                Path(path).write_bytes(raw)


@dataclass
class JsonFile(File[dict]):
    raw: Optional[Union[dict, bytes]] = None

    extension = ".json"

    def to_content(self, raw: bytes) -> dict:
        return json.loads(raw.decode())

    def to_bytes(self, content: dict) -> bytes:
        return dump_json(content).encode()


class FileContainer(Dict[str, FileType]):
    __slots__ = ("namespace",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.namespace = None

    def __setitem__(self, path: str, item: FileType):
        super().__setitem__(path, item)
        if self.namespace:
            item.bind(self.namespace, path)

    def update(self, mapping: Mapping[str, FileType]):  # type: ignore
        for path, item in mapping.items():
            self[path] = item

    def bind(self, namespace: Any):
        self.namespace = namespace
        for path, item in self.items():
            item.bind(namespace, path)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {list(self.keys())}>"


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


class FileContainerProxyDescriptor(Generic[FileType]):
    name: str

    def __set_name__(self, owner, name: str):
        self.name = name

    def __get__(self, instance: Any, owner=None) -> FileContainerProxy[FileType]:
        if owner is None:
            raise AttributeError(self.name)
        return FileContainerProxy(instance, self.name)


@dataclass
class Namespace(Dict[Type[File], FileContainer]):
    pack: Optional[Any] = extra_field(default=None, init=False)
    name: Optional[str] = extra_field(default=None, init=False)

    directory: ClassVar[str]
    path_mapping: ClassVar[Dict[Tuple[Tuple[str, ...], str], Type[File]]]
    container_fields: ClassVar[Dict[Type[File], str]]

    def __init_subclass__(cls: Type["Namespace"]):
        cls.container_fields = {
            get_args(hint)[0]: attr
            for attr, hint in get_type_hints(cls).items()
            if get_origin(hint) is FileContainer
        }
        cls.path_mapping = {
            (file_type.path, file_type.extension): file_type
            for file_type in cls.container_fields
        }

    def __post_init__(self):
        for file_type, attr in self.container_fields.items():
            super().__setitem__(file_type, getattr(self, attr))

    def __setitem__(self, key: str, item: File):  # type: ignore
        self[type(item)][key] = item

    def update(self, mapping: Mapping[str, File]):  # type: ignore
        for key, item in mapping.items():
            self[key] = item

    def merge(self, other: Mapping[Type[File], FileContainer]):
        for file_type, container in self.items():
            container.update(other[file_type])

    def all_files(self) -> Iterator[Tuple[str, File]]:
        for container in self.values():
            yield from container.items()

    def bind(self, pack: Any, name: str):
        self.pack = pack
        self.name = name

        for container in self.values():
            container.bind(self)

    @classmethod
    def load_from(
        cls: Type[NamespaceType], pack: PackOrigin
    ) -> Iterator[Tuple[str, NamespaceType]]:
        if isinstance(pack, ZipFile):
            filenames = map(PurePath, pack.namelist())
        else:
            filenames = list_files(pack)

        name = None
        namespace = None

        for filename in sorted(filenames):
            try:
                directory, namespace_dir, head, *rest, _basename = filename.parts
            except ValueError:
                continue

            if directory != cls.directory:
                continue
            if name != namespace_dir:
                if name and namespace:
                    yield name, namespace
                name = namespace_dir
                namespace = cls()

            assert name and namespace is not None
            extension = filename.suffix

            for path in accumulate(
                rest, lambda a, b: a + (b,), initial=cast(Tuple[str, ...], (head,))
            ):
                if file_type := cls.path_mapping.get((path, extension)):
                    key = "/".join(
                        filename.relative_to(Path(directory, name, *path))
                        .with_suffix("")
                        .parts
                    )
                    namespace[file_type][key] = (
                        file_type.load(str(filename), pack)
                        if isinstance(pack, ZipFile)
                        else file_type.load(pack / filename)
                    )

        if name and namespace:
            yield name, namespace

    def dump(self, namespace: str, pack: PackOrigin):
        for content_type, container in self.items():
            if not container:
                continue

            path = (self.directory, namespace) + content_type.path

            for name, item in container.items():
                full_path = path + (name + content_type.extension,)

                if isinstance(pack, ZipFile):
                    item.dump("/".join(full_path), pack)
                else:
                    filename = Path(pack, *full_path).resolve()
                    filename.parent.mkdir(parents=True, exist_ok=True)
                    item.dump(filename)

    def __ne__(self, obj: object) -> bool:
        return not self == obj

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
    eager: bool = extra_field(default=False)

    namespace_type: ClassVar[Type[NamespaceType]]
    latest_pack_format: ClassVar[int]

    def __init_subclass__(cls: Type["Pack"]):
        cls.namespace_type = get_args(getattr(cls, "__orig_bases__")[0])[0]

    def __post_init__(self):
        self.namespaces = self.items()
        self.load(eager=self.eager)

    def __missing__(self, name: str) -> NamespaceType:
        namespace = self.namespace_type()
        self[name] = namespace
        return namespace

    def __setitem__(self, key: str, item: Union[NamespaceType, File]):
        if isinstance(item, File):
            attr = self.namespace_type.container_fields[type(item)]
            getattr(self, attr)[key] = item
        else:
            super().__setitem__(key, item)
            item.bind(self, key)

    def update(self, mapping: Mapping[str, NamespaceType]):  # type: ignore
        for key, item in mapping.items():
            self[key] = item

    def merge(self, other: Mapping[str, NamespaceType]):
        for name, namespace in other.items():
            self[name].merge(namespace)

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

    def all_files(self) -> Iterator[Tuple[str, File]]:
        for name, namespace in self.items():
            for path, pack_file in namespace.all_files():
                yield f"{name}:{path}", pack_file

    def load(self, pack: PackOrigin = None, eager: bool = False):
        if pack is not None:
            if isinstance(pack, ZipFile):
                self.zipfile = pack
            elif not os.path.exists(pack):
                raise FileNotFoundError(pack)
            else:
                self.path = pack

        path = Path(self.path).resolve() if self.path else None

        if not self.name:
            self.name = (
                self.zipfile.filename if self.zipfile else path.stem if path else None
            )
        if self.zipped is None:
            self.zipped = bool(self.zipfile) or (
                path.suffix == ".zip" if path else False
            )

        origin: Union[Path, ZipFile, None] = self.zipfile

        if not origin and path:
            if path.is_file():
                origin = ZipFile(path)
            elif path.is_dir():
                origin = path

        if origin:
            if isinstance(origin, ZipFile):
                self.mcmeta = json.loads(origin.read("pack.mcmeta").decode())
            else:
                self.mcmeta = json.loads((origin / "pack.mcmeta").read_text())

            for name, namespace in self.namespace_type.load_from(origin):
                self[name].merge(namespace)

        if not self.pack_format:
            self.pack_format = self.latest_pack_format

        if eager:
            for _, pack_file in self.all_files():
                assert pack_file.content is not None

    def dump(
        self,
        directory: FileSystemPath = None,
        *,
        zipped: bool = None,
        overwrite: bool = False,
    ) -> Path:
        assert self.name

        if not directory:
            directory = Path(self.path).parent if self.path else Path.cwd()

        path = Path(directory).resolve()

        if zipped is None:
            zipped = bool(self.zipped)

        pack_factory: Any

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
            mcmeta = dump_json(self.mcmeta)

            if isinstance(pack, ZipFile):
                pack.writestr("pack.mcmeta", mcmeta)
            else:
                pack.mkdir(parents=True)
                (pack / "pack.mcmeta").write_text(mcmeta)

            for namespace_name, namespace in self.items():
                namespace.dump(namespace_name, pack)

        return output_path

    def __ne__(self, obj: object) -> bool:
        return not self == obj

    def __bool__(self) -> bool:
        return any(self.values())
