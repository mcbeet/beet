__all__ = [
    "Pack",
    "PackFile",
    "ExtraContainer",
    "SupportsExtra",
    "ExtraPin",
    "NamespaceExtraContainer",
    "PackExtraContainer",
    "McmetaPin",
    "PackPin",
    "Namespace",
    "NamespaceFile",
    "NamespaceContainer",
    "NamespacePin",
    "NamespaceProxy",
    "NamespaceProxyDescriptor",
    "MergeCallback",
    "MergePolicy",
    "PACK_COMPRESSION",
]


import shutil
from collections import defaultdict
from contextlib import nullcontext
from dataclasses import dataclass, field
from functools import partial
from itertools import count
from pathlib import Path, PurePosixPath
from typing import (
    Any,
    Callable,
    ClassVar,
    DefaultDict,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Literal,
    Mapping,
    MutableMapping,
    Optional,
    Protocol,
    Set,
    Tuple,
    Type,
    TypeVar,
    get_args,
    get_origin,
    overload,
)
from zipfile import ZIP_BZIP2, ZIP_DEFLATED, ZIP_LZMA, ZIP_STORED, ZipFile

from beet.core.container import (
    Container,
    ContainerProxy,
    Drop,
    MatchMixin,
    MergeMixin,
    Pin,
    SupportsMerge,
)
from beet.core.file import File, FileOrigin, JsonFile, PngFile
from beet.core.utils import FileSystemPath, JsonDict, TextComponent

from .utils import list_extensions, list_files

T = TypeVar("T")
PinType = TypeVar("PinType", covariant=True)
PackFileType = TypeVar("PackFileType", bound="PackFile")
NamespaceType = TypeVar("NamespaceType", bound="Namespace")
NamespaceFileType = TypeVar("NamespaceFileType", bound="NamespaceFile")
PackType = TypeVar("PackType", bound="Pack[Any]")
MergeableType = TypeVar("MergeableType", bound=SupportsMerge)

PackFile = File[Any, Any]


PACK_COMPRESSION: Dict[str, int] = {
    "none": ZIP_STORED,
    "deflate": ZIP_DEFLATED,
    "bzip2": ZIP_BZIP2,
    "lzma": ZIP_LZMA,
}


class NamespaceFile(PackFile):
    """Base class for files that belong in pack namespaces."""

    scope: ClassVar[Tuple[str, ...]]
    extension: ClassVar[str]


class MergeCallback(Protocol):
    """Protocol for detecting merge callbacks."""

    def __call__(self, pack: Any, path: str, current: Any, conflict: Any) -> bool:
        ...


@dataclass
class MergePolicy:
    """Class holding lists of rules for merging files."""

    extra: Dict[str, List[MergeCallback]] = field(default_factory=dict)
    namespace: Dict[Type[NamespaceFile], List[MergeCallback]] = field(
        default_factory=dict
    )
    namespace_extra: Dict[str, List[MergeCallback]] = field(default_factory=dict)

    def extend(self, other: "MergePolicy"):
        for rules, other_rules in [
            (self.extra, other.extra),
            (self.namespace, other.namespace),
            (self.namespace_extra, other.namespace_extra),
        ]:
            for key, value in other_rules.items():
                rules.setdefault(key, []).extend(value)  # type: ignore

    def extend_extra(self, filename: str, rule: MergeCallback):
        """Add rule for merging extra files."""
        self.extra.setdefault(filename, []).append(rule)

    def extend_namespace(self, file_type: Type[NamespaceFile], rule: MergeCallback):
        """Add rule for merging namespace files."""
        self.namespace.setdefault(file_type, []).append(rule)

    def extend_namespace_extra(self, filename: str, rule: MergeCallback):
        """Add rule for merging namespace extra files."""
        self.namespace_extra.setdefault(filename, []).append(rule)

    def merge_with_rules(
        self,
        pack: Any,
        current: MutableMapping[Any, SupportsMerge],
        other: Mapping[Any, SupportsMerge],
        map_rules: Callable[[str], Tuple[str, List[MergeCallback]]],
    ) -> bool:
        """Merge values according to the given rules."""
        for key, value in other.items():
            if key not in current:
                current[key] = value
                continue

            current_value = current[key]
            path, rules = map_rules(key)

            try:
                for rule in rules:
                    if rule(pack, path, current_value, value):
                        break
                else:
                    if not current_value.merge(value):
                        current[key] = value
            except Drop:
                del current[key]

        return True


class ExtraContainer(MatchMixin, MergeMixin, Container[str, PackFile]):
    """Container that stores extra files in a pack or a namespace."""


class SupportsExtra(Protocol):
    """Protocol for detecting extra container."""

    extra: ExtraContainer


class ExtraPin(Pin[str, PinType]):
    """Descriptor that makes a specific file accessible through attribute lookup."""

    def forward(self, obj: SupportsExtra) -> ExtraContainer:
        return obj.extra


class NamespaceExtraContainer(ExtraContainer, Generic[NamespaceType]):
    """Namespace extra container."""

    namespace: Optional[NamespaceType] = None

    def process(self, key: str, value: PackFile) -> PackFile:
        if (
            self.namespace is not None
            and self.namespace.pack is not None
            and self.namespace.name
        ):
            value.bind(self.namespace.pack, f"{self.namespace.name}:{key}")
        return value

    def bind(self, namespace: NamespaceType):
        """Handle insertion."""
        self.namespace = namespace

        for key, value in self.items():
            try:
                self.process(key, value)
            except Drop:
                del self[key]

    def merge(self, other: Mapping[Any, SupportsMerge]) -> bool:
        if (
            self.namespace is not None
            and self.namespace.pack is not None
            and self.namespace.name
        ):
            pack = self.namespace.pack
            name = self.namespace.name

            return pack.merge_policy.merge_with_rules(
                pack=pack,
                current=self,
                other=other,
                map_rules=lambda key: (
                    f"{name}:{key}",
                    pack.merge_policy.namespace_extra.get(key, []),
                ),
            )
        return super().merge(other)


class PackExtraContainer(ExtraContainer, Generic[PackType]):
    """Pack extra container."""

    pack: Optional[PackType] = None

    def process(self, key: str, value: PackFile) -> PackFile:
        if self.pack is not None:
            value.bind(self.pack, key)
        return value

    def bind(self, pack: PackType):
        """Handle insertion."""
        self.pack = pack

        for key, value in self.items():
            try:
                self.process(key, value)
            except Drop:
                del self[key]

    def merge(self, other: Mapping[Any, SupportsMerge]) -> bool:
        if self.pack is not None:
            pack = self.pack

            return pack.merge_policy.merge_with_rules(
                pack=pack,
                current=self,
                other=other,
                map_rules=lambda key: (
                    key,
                    pack.merge_policy.extra.get(key, []),
                ),
            )
        return super().merge(other)


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
            value.bind(self.namespace.pack, f"{self.namespace.name}:{key}")
        return value

    def bind(self, namespace: "Namespace", file_type: Type[NamespaceFileType]):
        """Handle insertion."""
        self.namespace = namespace
        self.file_type = file_type

        for key, value in self.items():
            try:
                self.process(key, value)
            except Drop:
                del self[key]

    def merge(self, other: Mapping[Any, SupportsMerge]) -> bool:
        if (
            self.namespace is not None
            and self.namespace.pack is not None
            and self.namespace.name
            and self.file_type is not None
        ):
            pack = self.namespace.pack
            name = self.namespace.name
            file_type = self.file_type

            return pack.merge_policy.merge_with_rules(
                pack=pack,
                current=self,  # type: ignore
                other=other,
                map_rules=lambda key: (
                    f"{name}:{key}",
                    pack.merge_policy.namespace.get(file_type, []),
                ),
            )
        return super().merge(other)

    def generate_tree(self, path: str = "") -> Dict[Any, Any]:
        """Generate a hierarchy of nested dictionaries representing the files and folders."""
        prefix = path.split("/") if path else []
        tree: Dict[Any, Any] = {}

        for filename, file_instance in self.items():
            parts = filename.split("/")

            if parts[: len(prefix)] != prefix:
                continue

            parent = tree
            for part in parts[len(prefix) :]:
                parent = parent.setdefault(part, {})

            parent[self.file_type] = file_instance

        return tree


class NamespacePin(Pin[Type[NamespaceFileType], NamespaceContainer[NamespaceFileType]]):
    """Descriptor for accessing namespace containers by attribute lookup."""


class Namespace(
    MergeMixin, Container[Type[NamespaceFile], NamespaceContainer[NamespaceFile]]
):
    """Class representing a namespace."""

    pack: Optional["Pack[Namespace]"] = None
    name: Optional[str] = None
    extra: NamespaceExtraContainer["Namespace"]

    directory: ClassVar[str]
    field_map: ClassVar[Mapping[Type[NamespaceFile], str]]
    scope_map: ClassVar[Mapping[Tuple[Tuple[str, ...], str], Type[NamespaceFile]]]

    def __init_subclass__(cls):
        pins = NamespacePin[NamespaceFileType].collect_from(cls)
        cls.field_map = {pin.key: attr for attr, pin in pins.items()}
        cls.scope_map = {
            (pin.key.scope, pin.key.extension): pin.key for pin in pins.values()
        }

    def __init__(self):
        super().__init__()
        self.extra = NamespaceExtraContainer()

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

        self.extra.bind(self)

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
        if type(self) == type(other) and not self.extra == other.extra:
            return False
        if isinstance(other, Mapping):
            rhs: Mapping[Type[NamespaceFile], NamespaceContainer[NamespaceFile]] = other
            return all(self[key] == rhs[key] for key in self.keys() | rhs.keys())
        return NotImplemented

    def __bool__(self) -> bool:
        return any(self.values()) or bool(self.extra)

    def missing(self, key: Type[NamespaceFile]) -> NamespaceContainer[NamespaceFile]:
        return NamespaceContainer()

    def merge(
        self: MutableMapping[T, MergeableType],  # type: ignore
        other: Mapping[T, MergeableType],
    ) -> bool:
        super().merge(other)  # type: ignore

        if isinstance(self, Namespace) and isinstance(other, Namespace):
            self.extra.merge(other.extra)

        empty_containers = [key for key, value in self.items() if not value]  # type: ignore
        for container in empty_containers:
            del self[container]  # type: ignore

        return True

    @property
    def content(self) -> Iterator[Tuple[str, NamespaceFile]]:
        """Iterator that yields all the files stored in the namespace."""
        for container in self.values():
            yield from container.items()

    @overload
    def list_files(
        self,
        namespace: str,
        *extensions: str,
    ) -> Iterator[Tuple[str, PackFile]]:
        ...

    @overload
    def list_files(
        self,
        namespace: str,
        *extensions: str,
        extend: Type[T],
    ) -> Iterator[Tuple[str, T]]:
        ...

    def list_files(
        self, namespace: str, *extensions: str, extend: Optional[Any] = None
    ) -> Iterator[Tuple[str, Any]]:
        """List and filter all the files in the namespace."""
        if extend and (origin := get_origin(extend)):
            extend = origin

        for path, item in self.extra.items():
            if item is None:
                continue
            if extensions and not any(path.endswith(ext) for ext in extensions):
                continue
            if extend and not isinstance(item, extend):
                continue
            yield f"{self.directory}/{namespace}/{path}", item

        for content_type, container in self.items():
            if not container:
                continue
            if extensions and content_type.extension not in extensions:
                continue
            prefix = "/".join((self.directory, namespace) + content_type.scope)
            for name, item in container.items():
                if extend and not isinstance(item, extend):
                    continue
                yield f"{prefix}/{name}{content_type.extension}", item

    @classmethod
    def get_extra_info(cls) -> Dict[str, Type[PackFile]]:
        return {}

    @classmethod
    def scan(
        cls,
        pack: FileOrigin,
        extend_namespace: Iterable[Type[NamespaceFile]] = (),
        extend_namespace_extra: Optional[Mapping[str, Type[PackFile]]] = None,
    ) -> Iterator[Tuple[str, "Namespace"]]:
        """Load namespaces by walking through a zipfile or directory."""
        name, namespace = None, None
        filenames = (
            map(PurePosixPath, pack.namelist())
            if isinstance(pack, ZipFile)
            else list_files(pack)
        )

        extra_info = cls.get_extra_info()
        if extend_namespace_extra:
            extra_info.update(extend_namespace_extra)

        scope_map = dict(cls.scope_map)
        for file_type in extend_namespace:
            scope_map[file_type.scope, file_type.extension] = file_type

        for filename in sorted(filenames):
            try:
                directory, namespace_dir, *scope, extra_name = filename.parts
            except ValueError:
                continue

            if directory != cls.directory:
                continue
            if name != namespace_dir:
                if name and namespace:
                    yield name, namespace
                name, namespace = namespace_dir, cls()

            assert name and namespace is not None
            extensions = list_extensions(filename)

            if file_type := extra_info.get(path := "/".join(scope + [extra_name])):
                namespace.extra[path] = file_type.load(pack, filename)
                continue

            while path := tuple(scope):
                for extension in extensions:
                    if file_type := scope_map.get((path, extension)):
                        key = "/".join(
                            filename.relative_to(Path(directory, name, *path)).parts
                        )[: -len(extension)]

                        namespace[file_type][key] = file_type.load(pack, filename)
                        break
                else:
                    scope.pop()
                    continue
                break

        if name and namespace:
            yield name, namespace

    def dump(self, namespace: str, origin: FileOrigin):
        """Write the namespace to a zipfile or to the filesystem."""
        _dump_files(origin, dict(self.list_files(namespace)))

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

    def walk(self) -> Iterator[Tuple[str, Set[str], Dict[str, NamespaceFileType]]]:
        """Walk over the file hierarchy."""
        for prefix, namespace in self.proxy.items():
            separator = ":"
            roots: List[Tuple[str, Dict[Any, Any]]] = [
                (prefix, namespace[self.proxy_key].generate_tree())  # type: ignore
            ]

            while roots:
                prefix, root = roots.pop()

                dirs: Set[str] = set()
                files: Dict[str, NamespaceFileType] = {}

                for key, value in root.items():
                    if not isinstance(key, str):
                        continue
                    if any(isinstance(name, str) for name in value):
                        dirs.add(key)
                    if file_instance := value.get(self.proxy_key, None):
                        files[key] = file_instance

                yield prefix + separator, dirs, files

                for directory in dirs:
                    roots.append((prefix + separator + directory, root[directory]))

                separator = "/"


@dataclass
class NamespaceProxyDescriptor(Generic[NamespaceFileType]):
    """Descriptor that dynamically instantiates a namespace proxy."""

    proxy_key: Type[NamespaceFileType]

    def __get__(
        self, obj: Any, objtype: Optional[Type[Any]] = None
    ) -> NamespaceProxy[NamespaceFileType]:
        return NamespaceProxy[NamespaceFileType](obj, self.proxy_key)


class McmetaPin(Pin[str, PinType]):
    """Descriptor that makes it possible to bind pack.mcmeta information to attribute lookup."""

    def forward(self, obj: "Pack[Namespace]") -> JsonDict:
        return obj.mcmeta.data


class PackPin(McmetaPin[PinType]):
    """Descriptor that makes pack metadata accessible through attribute lookup."""

    def forward(self, obj: "Pack[Namespace]") -> JsonDict:
        return super().forward(obj).setdefault("pack", {})


class Pack(MatchMixin, MergeMixin, Container[str, NamespaceType]):
    """Class representing a pack."""

    name: Optional[str]
    path: Optional[Path]
    zipped: bool
    compression: Optional[Literal["none", "deflate", "bzip2", "lzma"]]
    compression_level: Optional[int]

    extra: PackExtraContainer["Pack[NamespaceType]"]
    mcmeta: ExtraPin[JsonFile] = ExtraPin(
        "pack.mcmeta", default_factory=lambda: JsonFile({})
    )
    icon: ExtraPin[Optional[PngFile]] = ExtraPin("pack.png", default=None)

    description: PackPin[TextComponent] = PackPin("description", default="")
    pack_format: PackPin[int] = PackPin("pack_format", default=0)

    extend_extra: Dict[str, Type[PackFile]]
    extend_namespace: List[Type[NamespaceFile]]
    extend_namespace_extra: Dict[str, Type[PackFile]]

    merge_policy: MergePolicy

    namespace_type: ClassVar[Type[Namespace]]
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
        compression: Optional[Literal["none", "deflate", "bzip2", "lzma"]] = None,
        compression_level: Optional[int] = None,
        mcmeta: Optional[JsonFile] = None,
        icon: Optional[PngFile] = None,
        description: Optional[str] = None,
        pack_format: Optional[int] = None,
        extend_extra: Optional[Mapping[str, Type[PackFile]]] = None,
        extend_namespace: Iterable[Type[NamespaceFile]] = (),
        extend_namespace_extra: Optional[Mapping[str, Type[PackFile]]] = None,
        merge_policy: Optional[MergePolicy] = None,
    ):
        super().__init__()
        self.name = name
        self.path = None
        self.zipped = zipped
        self.compression = compression
        self.compression_level = compression_level

        self.extra = PackExtraContainer()
        self.extra.bind(self)

        if mcmeta is not None:
            self.mcmeta = mcmeta
        if icon is not None:
            self.icon = icon
        if description is not None:
            self.description = description
        if pack_format is not None:
            self.pack_format = pack_format

        self.extend_extra = dict(extend_extra or {})
        self.extend_namespace = list(extend_namespace)
        self.extend_namespace_extra = dict(extend_namespace_extra or {})

        self.merge_policy = MergePolicy()
        if merge_policy:
            self.merge_policy.extend(merge_policy)

        self.load(path or zipfile)

    def configure(
        self: PackType,
        other: Optional[PackType] = None,
        *,
        extend_extra: Optional[Mapping[str, Type[PackFile]]] = None,
        extend_namespace: Iterable[Type[NamespaceFile]] = (),
        extend_namespace_extra: Optional[Mapping[str, Type[PackFile]]] = None,
        merge_policy: Optional[MergePolicy] = None,
    ) -> PackType:
        """Helper for updating or copying configuration from another pack."""
        if other:
            self.extend_extra.update(other.extend_extra or {})
            self.extend_namespace.extend(other.extend_namespace)
            self.extend_namespace_extra.update(other.extend_namespace_extra or {})
            self.merge_policy.extend(other.merge_policy)

        self.extend_extra.update(extend_extra or {})
        self.extend_namespace.extend(extend_namespace)
        self.extend_namespace_extra.update(extend_namespace_extra or {})

        if merge_policy:
            self.merge_policy.extend(merge_policy)

        return self

    @overload
    def __getitem__(self, key: str) -> NamespaceType:
        ...

    @overload
    def __getitem__(
        self, key: Type[NamespaceFileType]
    ) -> NamespaceProxy[NamespaceFileType]:
        ...

    def __getitem__(self, key: Any) -> Any:
        if isinstance(key, str):
            return super().__getitem__(key)
        return NamespaceProxy(self, key)

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
            NamespaceProxy[NamespaceFile](self, type(value))[key] = value

    def __eq__(self, other: Any) -> bool:
        if type(self) == type(other) and not (
            self.name == other.name and self.extra == other.extra
        ):
            return False
        if isinstance(other, Mapping):
            rhs: Mapping[str, Namespace] = other
            return all(self[key] == rhs[key] for key in self.keys() | rhs.keys())
        return NotImplemented

    def __bool__(self) -> bool:
        return any(self.values()) or self.extra.keys() > {"pack.mcmeta"}

    def __enter__(self: T) -> T:
        return self

    def __exit__(self, *_):
        self.save(overwrite=True)

    def process(self, key: str, value: NamespaceType) -> NamespaceType:
        value.bind(self, key)  # type: ignore
        return value

    def missing(self, key: str) -> NamespaceType:
        return self.namespace_type()  # type: ignore

    def merge(
        self: MutableMapping[T, MergeableType], other: Mapping[T, MergeableType]
    ) -> bool:
        super().merge(other)  # type: ignore

        if isinstance(self, Pack) and isinstance(other, Pack):
            self.extra.merge(other.extra)  # type: ignore

        empty_namespaces = [key for key, value in self.items() if not value]  # type: ignore
        for namespace in empty_namespaces:
            del self[namespace]  # type: ignore

        return True

    @property
    def content(self) -> Iterator[Tuple[str, NamespaceFile]]:
        """Iterator that yields all the files stored in the pack."""
        for file_type in self.namespace_type.field_map:
            yield from NamespaceProxy[NamespaceFile](self, file_type).items()

    @overload
    def list_files(
        self,
        *extensions: str,
    ) -> Iterator[Tuple[str, PackFile]]:
        ...

    @overload
    def list_files(
        self,
        *extensions: str,
        extend: Type[T],
    ) -> Iterator[Tuple[str, T]]:
        ...

    def list_files(
        self,
        *extensions: str,
        extend: Optional[Any] = None,
    ) -> Iterator[Tuple[str, Any]]:
        """List and filter all the files in the pack."""
        if extend and (origin := get_origin(extend)):
            extend = origin

        for path, item in self.extra.items():
            if item is None:
                continue
            if extensions and not any(path.endswith(ext) for ext in extensions):
                continue
            if extend and not isinstance(item, extend):
                continue
            yield path, item

        for namespace_name, namespace in self.items():
            yield from namespace.list_files(namespace_name, *extensions, extend=extend)  # type: ignore

    @classmethod
    def get_extra_info(cls) -> Dict[str, Type[PackFile]]:
        return {"pack.mcmeta": JsonFile, "pack.png": PngFile}

    def resolve_extra_info(self) -> Dict[str, Type[PackFile]]:
        extra_info = self.get_extra_info()
        if self.extend_extra:
            extra_info.update(self.extend_extra)
        return extra_info

    def resolve_scope_map(
        self,
    ) -> Dict[Tuple[Tuple[str, ...], str], Type[NamespaceFile]]:
        scope_map = dict(self.namespace_type.scope_map)
        for file_type in self.extend_namespace:
            scope_map[file_type.scope, file_type.extension] = file_type
        return scope_map

    def resolve_namespace_extra_info(self) -> Dict[str, Type[PackFile]]:
        namespace_extra_info = self.namespace_type.get_extra_info()
        if self.extend_namespace_extra:
            namespace_extra_info.update(self.extend_namespace_extra)
        return namespace_extra_info

    def load(
        self,
        origin: Optional[FileOrigin] = None,
        extend_extra: Optional[Mapping[str, Type[PackFile]]] = None,
        extend_namespace: Iterable[Type[NamespaceFile]] = (),
        extend_namespace_extra: Optional[Mapping[str, Type[PackFile]]] = None,
        merge_policy: Optional[MergePolicy] = None,
    ):
        """Load pack from a zipfile or from the filesystem."""
        self.extend_extra.update(extend_extra or {})
        self.extend_namespace.extend(extend_namespace)
        self.extend_namespace_extra.update(extend_namespace_extra or {})

        if merge_policy:
            self.merge_policy.extend(merge_policy)

        if origin:
            if not isinstance(origin, ZipFile):
                origin = Path(origin).resolve()
                self.path = origin.parent
                if origin.is_file():
                    origin = ZipFile(origin)
                elif not origin.is_dir():
                    self.name = origin.name
                    self.zipped = origin.suffix == ".zip"
                    origin = None
            if isinstance(origin, ZipFile):
                self.zipped = True
                self.name = origin.filename and Path(origin.filename).name
            elif origin:
                self.zipped = False
                self.name = origin.name
            if self.name and self.name.endswith(".zip"):
                self.name = self.name[:-4]

        if origin:
            files = {
                filename: loaded
                for filename, file_type in self.resolve_extra_info().items()
                if (loaded := file_type.try_load(origin, filename))
            }

            self.extra.merge(files)

            namespaces = {
                name: namespace
                for name, namespace in self.namespace_type.scan(
                    origin,
                    self.extend_namespace,
                    self.extend_namespace_extra,
                )
            }

            self.merge(namespaces)  # type: ignore

        if not self.pack_format:
            self.pack_format = self.latest_pack_format
        if not self.description:
            self.description = ""

    def dump(self, origin: FileOrigin):
        """Write the content of the pack to a zipfile or to the filesystem"""
        extra = {path: item for path, item in self.extra.items() if item is not None}
        _dump_files(origin, extra)

        for namespace_name, namespace in self.items():
            namespace.dump(namespace_name, origin)

    def save(
        self,
        directory: Optional[FileSystemPath] = None,
        path: Optional[FileSystemPath] = None,
        zipped: Optional[bool] = None,
        compression: Optional[Literal["none", "deflate", "bzip2", "lzma"]] = None,
        compression_level: Optional[int] = None,
        overwrite: Optional[bool] = False,
    ) -> Path:
        """Save the pack at the specified location."""
        if path:
            path = Path(path).resolve()
            self.zipped = path.suffix == ".zip"
            self.name = path.name[:-4] if self.zipped else path.name
            self.path = path.parent

        if zipped is not None:
            self.zipped = zipped
        if compression is not None:
            self.compression = compression
        if compression_level is not None:
            self.compression_level = compression_level

        suffix = ".zip" if self.zipped else ""
        factory: Any = (
            partial(
                ZipFile,
                mode="w",
                compression=PACK_COMPRESSION[self.compression or "deflate"],
                compresslevel=self.compression_level,
            )
            if self.zipped
            else nullcontext
        )

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
