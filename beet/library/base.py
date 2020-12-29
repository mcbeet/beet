__all__ = [
    "Pack",
    "PackFile",
    "PackContainer",
    "PackPin",
    "McmetaPin",
    "Namespace",
    "NamespaceFile",
    "NamespaceContainer",
    "NamespacePin",
    "NamespaceProxy",
    "NamespaceProxyDescriptor",
]


import shutil
from collections import defaultdict
from contextlib import nullcontext
from dataclasses import dataclass
from functools import partial
from itertools import accumulate, count
from pathlib import Path, PurePosixPath
from typing import (
    Any,
    ClassVar,
    DefaultDict,
    Dict,
    Generic,
    Iterator,
    List,
    Mapping,
    Optional,
    Tuple,
    Type,
    TypeVar,
    get_args,
    overload,
)
from zipfile import ZipFile

from beet.core.container import (
    Container,
    ContainerProxy,
    MatchMixin,
    MergeMixin,
    Pin,
    PinDefault,
    PinDefaultFactory,
)
from beet.core.file import File, FileOrigin, JsonFile, PngFile
from beet.core.utils import SENTINEL_OBJ, FileSystemPath, JsonDict

from .utils import list_files

T = TypeVar("T")
PackFileType = TypeVar("PackFileType", bound="PackFile")
NamespaceType = TypeVar("NamespaceType", bound="Namespace")
NamespaceFileType = TypeVar("NamespaceFileType", bound="NamespaceFile")

PackFile = File[Any, Any]


class NamespaceFile(PackFile):
    """Base class for files that belong in pack namespaces."""

    scope: ClassVar[Tuple[str, ...]]
    extension: ClassVar[str]

    def bind(self, pack: Any, namespace: str, path: str):
        """Handle insertion."""


class NamespaceContainer(MatchMixin, MergeMixin, Container[str, NamespaceFileType]):
    """Container that stores one type of files in a namespace."""

    namespace: Optional["Namespace"] = None
    file_type: Optional[Type[NamespaceFileType]] = None

    def process(self, key: str, value: NamespaceFileType) -> NamespaceFileType:
        if (
            self.namespace is not None
            and self.namespace.pack is not None
            and self.namespace.name
        ):
            value.bind(self.namespace.pack, self.namespace.name, key)
        return value

    def bind(self, namespace: "Namespace", file_type: Type[NamespaceFileType]):
        """Handle insertion."""
        self.namespace = namespace
        self.file_type = file_type

        for key, value in self.items():
            self.process(key, value)


@dataclass
class NamespacePin(Pin[NamespaceContainer[NamespaceFileType]]):
    """Descriptor for accessing namespace containers by attribute lookup."""

    key: Type[NamespaceFileType]


class Namespace(
    MergeMixin, Container[Type[NamespaceFile], NamespaceContainer[NamespaceFile]]
):
    """Class representing a namespace."""

    pack: Optional["Pack[Namespace]"] = None
    name: Optional[str] = None

    directory: ClassVar[str]
    field_map: ClassVar[Mapping[Type[NamespaceFile], str]]
    scope_map: ClassVar[Mapping[Tuple[Tuple[str, ...], str], Type[NamespaceFile]]]

    def __init_subclass__(cls):
        pins = NamespacePin[NamespaceFile].collect_from(cls)
        cls.field_map = {pin.key: attr for attr, pin in pins.items()}
        cls.scope_map = {
            (pin.key.scope, pin.key.extension): pin.key for pin in pins.values()
        }

    def process(
        self, key: Type[NamespaceFile], value: NamespaceContainer[NamespaceFile]
    ) -> NamespaceContainer[NamespaceFile]:
        value.bind(self, key)
        return value

    def bind(self, pack: "Pack[Namespace]", name: str):
        """Handle insertion."""
        self.pack = pack
        self.name = name

        for key, value in self.items():
            self.process(key, value)

    @overload
    def __setitem__(
        self, key: Type[NamespaceFile], value: NamespaceContainer[NamespaceFile]
    ):
        ...

    @overload
    def __setitem__(self, key: str, value: NamespaceFile):
        ...

    def __setitem__(self, key: Any, value: Any):
        if isinstance(key, type):
            super().__setitem__(key, value)  # type: ignore
        else:
            self[type(value)][key] = value

    def __eq__(self, other: Any) -> bool:
        return all(self[key] == other[key] for key in self.field_map)

    def __bool__(self) -> bool:
        return any(self.values())

    def missing(self, key: Type[NamespaceFile]) -> NamespaceContainer[NamespaceFile]:
        return NamespaceContainer()

    @property
    def content(self) -> Iterator[Tuple[str, NamespaceFile]]:
        """Iterator that yields all the files stored in the namespace."""
        for container in self.values():
            yield from container.items()

    @classmethod
    def scan(cls, pack: FileOrigin) -> Iterator[Tuple[str, "Namespace"]]:
        """Load namespaces by walking through a zipfile or directory."""
        name, namespace = None, None
        filenames = (
            map(PurePosixPath, pack.namelist())
            if isinstance(pack, ZipFile)
            else list_files(pack)
        )

        for filename in sorted(filenames):
            try:
                directory, namespace_dir, head, *rest, _ = filename.parts
            except ValueError:
                continue

            if directory != cls.directory:
                continue
            if name != namespace_dir:
                if name and namespace:
                    yield name, namespace
                name, namespace = namespace_dir, cls()

            assert name and namespace is not None
            extension = "".join(filename.suffixes)

            for path in accumulate(rest, lambda a, b: a + (b,), initial=(head,)):
                if file_type := cls.scope_map.get((path, extension)):
                    key = "/".join(
                        filename.relative_to(Path(directory, name, *path)).parts
                    )[: -len(extension)]

                    namespace[file_type][key] = file_type.load(pack, filename)

        if name and namespace:
            yield name, namespace

    def dump(self, namespace: str, origin: FileOrigin):
        """Write the namespace to a zipfile or to the filesystem."""
        _dump_files(
            origin,
            {
                "/".join((self.directory, namespace) + content_type.scope)
                + f"/{name}{content_type.extension}": item
                for content_type, container in self.items()
                if container
                for name, item in container.items()
            },
        )

    def __repr__(self) -> str:
        args = ", ".join(
            f"{self.field_map[key]}={value}" for key, value in self.items() if value
        )
        return f"{self.__class__.__name__}({args})"


class NamespaceProxy(
    MatchMixin,
    MergeMixin,
    ContainerProxy[Type[NamespaceFileType], str, NamespaceFileType],
):
    """Aggregated view that exposes a certain type of files over all namespaces."""

    def split_key(self, key: str) -> Tuple[str, str]:
        namespace, _, file_path = key.partition(":")
        if not file_path:
            raise KeyError(key)
        return namespace, file_path

    def join_key(self, key1: str, key2: str) -> str:
        return f"{key1}:{key2}"


@dataclass
class NamespaceProxyDescriptor(Generic[NamespaceFileType]):
    """Descriptor that dynamically instantiates a namespace proxy."""

    proxy_key: Type[NamespaceFileType]

    def __get__(
        self, obj: Any, objtype: Optional[Type[Any]] = None
    ) -> NamespaceProxy[NamespaceFileType]:
        return NamespaceProxy(obj, self.proxy_key)


class PackContainer(MatchMixin, MergeMixin, Container[str, PackFile]):
    """Container that stores non-namespaced files in a pack."""

    def __bool__(self) -> bool:
        return any(self.values())


@dataclass
class PackPin(Pin[T]):
    """Descriptor that makes a specific file accessible through attribute lookup."""

    key: str
    default: PinDefault[T] = SENTINEL_OBJ
    default_factory: PinDefaultFactory[T] = SENTINEL_OBJ

    def forward(self, obj: "Pack[Namespace]") -> PackContainer:
        return obj.extra


@dataclass
class McmetaPin(Pin[T]):
    """Descriptor that makes it possible to bind pack.mcmeta information to attribute lookup."""

    key: str
    default: PinDefault[T] = SENTINEL_OBJ
    default_factory: PinDefaultFactory[T] = SENTINEL_OBJ

    def forward(self, obj: "Pack[Namespace]") -> JsonDict:
        return obj.mcmeta.data.setdefault("pack", {})


class Pack(MatchMixin, MergeMixin, Container[str, NamespaceType]):
    """Class representing a pack."""

    name: Optional[str]
    path: Optional[Path]
    zipped: bool

    extra: PackContainer
    mcmeta = PackPin[JsonFile]("pack.mcmeta", default_factory=lambda: JsonFile({}))
    image = PackPin[Optional[PngFile]]("pack.png", default=None)

    description = McmetaPin[str]("description", default="")
    pack_format = McmetaPin[int]("pack_format", default=0)

    namespace_type: ClassVar[Type[NamespaceType]]
    default_name: ClassVar[str]
    latest_pack_format: ClassVar[int]

    def __init_subclass__(cls):
        cls.namespace_type = get_args(getattr(cls, "__orig_bases__")[0])[0]

    def __init__(
        self,
        name: Optional[str] = None,
        path: Optional[FileSystemPath] = None,
        zipfile: Optional[ZipFile] = None,
        zipped: bool = False,
        mcmeta: Optional[JsonFile] = None,
        image: Optional[PngFile] = None,
        description: Optional[str] = None,
        pack_format: Optional[int] = None,
    ):
        super().__init__()
        self.name = name
        self.path = None
        self.zipped = zipped

        self.extra = PackContainer()

        if mcmeta is not None:
            self.mcmeta = mcmeta
        if image is not None:
            self.image = image
        if description is not None:
            self.description = description
        if pack_format is not None:
            self.pack_format = pack_format

        self.load(path or zipfile)

    @overload
    def __setitem__(self, key: str, value: NamespaceType):
        ...

    @overload
    def __setitem__(self, key: str, value: NamespaceFile):
        ...

    def __setitem__(self, key: str, value: Any):
        if isinstance(value, Namespace):
            super().__setitem__(key, value)  # type: ignore
        else:
            NamespaceProxy(self, type(value))[key] = value

    def __eq__(self, other: Any) -> bool:
        if type(self) != type(other):
            return NotImplemented
        return (
            self.name == other.name
            and self.extra == other.extra
            and all(self[key] == other[key] for key in self.keys() | other.keys())
        )

    def __bool__(self) -> bool:
        return any(self.values())

    def __enter__(self: T) -> T:
        return self

    def __exit__(self, *_):
        self.save(overwrite=True)

    def process(self, key: str, value: NamespaceType) -> NamespaceType:
        value.bind(self, key)
        return value

    def missing(self, key: str) -> NamespaceType:
        return self.namespace_type()

    @property
    def content(self) -> Iterator[Tuple[str, NamespaceFile]]:
        """Iterator that yields all the files stored in the pack."""
        for file_type in self.namespace_type.field_map:
            yield from NamespaceProxy(self, file_type).items()

    @classmethod
    def get_extra_info(cls) -> Dict[str, Type[PackFile]]:
        return {"pack.mcmeta": JsonFile, "pack.png": PngFile}

    def load(self, origin: Optional[FileOrigin] = None):
        """Load pack from a zipfile or from the filesystem."""
        if origin:
            if not isinstance(origin, ZipFile):
                origin = Path(origin).resolve()
                self.path = origin.parent
                if origin.is_file():
                    origin = ZipFile(origin)
                elif not origin.is_dir():
                    self.name = origin.stem
                    self.zipped = origin.suffix == ".zip"
                    origin = None
            if isinstance(origin, ZipFile):
                self.zipped = True
                self.name = origin.filename and Path(origin.filename).stem
            elif origin:
                self.zipped = False
                self.name = origin.stem

        if origin:
            files = {
                filename: loaded
                for filename, file_type in self.get_extra_info().items()
                if (loaded := file_type.try_load(origin, filename))
            }

            self.extra.merge(files)

            namespaces = {
                name: namespace for name, namespace in self.namespace_type.scan(origin)
            }

            self.merge(namespaces)

        if not self.pack_format:
            self.pack_format = self.latest_pack_format
        if not self.description:
            self.description = ""

    def dump(self, origin: FileOrigin):
        """Write the content of the pack to a zipfile or to the filesystem """
        extra = {path: item for path, item in self.extra.items() if item is not None}
        _dump_files(origin, extra)

        for namespace_name, namespace in self.items():
            namespace.dump(namespace_name, origin)

    def save(
        self,
        directory: Optional[FileSystemPath] = None,
        zipped: Optional[bool] = None,
        overwrite: Optional[bool] = False,
    ) -> Path:
        """Save the pack at the specified location."""
        if zipped is not None:
            self.zipped = zipped
        suffix = ".zip" if self.zipped else ""
        factory = partial(ZipFile, mode="w") if self.zipped else nullcontext

        if not directory:
            directory = self.path or Path.cwd()

        self.path = Path(directory).resolve()

        if not self.name:
            for i in count():
                self.name = self.default_name + (str(i) if i else "")
                if not (self.path / f"{self.name}{suffix}").exists():
                    break

        output_path = self.path / f"{self.name}{suffix}"

        if output_path.exists():
            if not overwrite:
                raise FileExistsError(f"Couldn't overwrite {str(output_path)!r}.")
            if output_path.is_dir():
                shutil.rmtree(output_path)
            else:
                output_path.unlink()

        if self.zipped:
            self.path.mkdir(parents=True, exist_ok=True)
        else:
            output_path.mkdir(parents=True, exist_ok=True)

        with factory(output_path) as pack:
            self.dump(pack)

        return output_path

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(name={self.name!r}, "
            f"description={self.description!r}, pack_format={self.pack_format!r})"
        )


def _dump_files(origin: FileOrigin, files: Mapping[str, PackFile]):
    dirs: DefaultDict[Tuple[str, ...], List[Tuple[str, PackFile]]] = defaultdict(list)

    for full_path, item in files.items():
        directory, _, filename = full_path.rpartition("/")
        dirs[(directory,) if directory else ()].append((filename, item))

    for directory, entries in dirs.items():
        if not isinstance(origin, ZipFile):
            Path(origin, *directory).resolve().mkdir(parents=True, exist_ok=True)
        for (filename, f) in entries:
            f.dump(origin, "/".join(directory + (filename,)))
