__all__ = [
    "Pack",
    "PackFile",
    "ExtraContainer",
    "SupportsExtra",
    "ExtraPin",
    "NamespaceExtraContainer",
    "PackExtraContainer",
    "Mcmeta",
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
    "OverlayContainer",
    "UnveilMapping",
    "PackOverwrite",
    "PACK_COMPRESSION",
    "LATEST_MINECRAFT_VERSION",
]


import shutil
from collections import defaultdict
from contextlib import nullcontext
from dataclasses import dataclass, field
from functools import partial
from itertools import count
from pathlib import Path, PurePath, PurePosixPath
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
    Union,
    get_args,
    get_origin,
    overload,
)
from zipfile import ZIP_BZIP2, ZIP_DEFLATED, ZIP_LZMA, ZIP_STORED, ZipFile

from typing_extensions import Self

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
from beet.core.utils import FileSystemPath, JsonDict, SupportedFormats, TextComponent

from .utils import list_extensions, list_origin_folders

LATEST_MINECRAFT_VERSION: str = "1.20"


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


class NamespaceFile(Protocol):
    """Protocol for detecting files that belong in pack namespaces."""

    scope: ClassVar[Tuple[str, ...]]
    extension: ClassVar[str]

    snake_name: ClassVar[str]

    def __init__(
        self,
        _content: Optional[Any] = None,
        /,
        *,
        source_path: Optional[FileSystemPath] = None,
        source_start: Optional[int] = None,
        source_stop: Optional[int] = None,
        on_bind: Optional[Callable[[Any, Any, str], Any]] = None,
        original: Any = None,
    ) -> None:
        ...

    def merge(self, other: Any) -> bool:
        ...

    def bind(self, pack: Any, path: str) -> Any:
        ...

    def set_content(self, content: Any):
        ...

    def get_content(self) -> Any:
        ...

    def ensure_source_path(self) -> FileSystemPath:
        ...

    def ensure_serialized(
        self,
        serializer: Optional[Callable[[Any], Any]] = None,
    ) -> Any:
        ...

    def ensure_deserialized(
        self,
        deserializer: Optional[Callable[[Any], Any]] = None,
    ) -> Any:
        ...

    @classmethod
    def default(cls) -> Any:
        ...

    @classmethod
    def load(cls: Type[T], origin: FileOrigin, path: FileSystemPath) -> T:
        ...

    def dump(self, origin: FileOrigin, path: FileSystemPath):
        ...


class MergeCallback(Protocol):
    """Protocol for detecting merge callbacks."""

    def __call__(self, pack: Any, path: str, current: Any, conflict: Any, /) -> bool:
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
                current=self,  # type: ignore
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
                current=self,  # type: ignore
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

    def setdefault(
        self,
        key: str,
        default: Optional[NamespaceFileType] = None,
    ) -> NamespaceFileType:
        if value := self.get(key):
            return value
        if default:
            self[key] = default
        else:
            if not self.file_type:
                raise ValueError(
                    "File type associated to the namespace container is not available."
                )
            self[key] = self.file_type()
        return self[key]

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
    MergeMixin,
    Container[Type[NamespaceFile], NamespaceContainer[NamespaceFile]],
):
    """Class representing a namespace."""

    pack: Optional["Pack[Namespace]"] = None
    name: Optional[str] = None
    extra: NamespaceExtraContainer["Namespace"]

    directory: ClassVar[str]
    field_map: ClassVar[Mapping[Type[NamespaceFile], str]]
    scope_map: ClassVar[Mapping[Tuple[Tuple[str, ...], str], Type[NamespaceFile]]]

    def __init_subclass__(cls):
        pins = NamespacePin[NamespaceFile].collect_from(cls)
        cls.field_map = {pin.key: attr for attr, pin in pins.items()}
        cls.scope_map = {
            (pin.key.scope, pin.key.extension): pin.key for pin in pins.values()
        }

    def __init__(self):
        super().__init__()
        self.extra = NamespaceExtraContainer()

    def process(
        self,
        key: Type[NamespaceFile],
        value: NamespaceContainer[NamespaceFile],
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
        self,
        key: Type[NamespaceFile],
        value: NamespaceContainer[NamespaceFile],
    ) -> None:
        ...

    @overload
    def __setitem__(self, key: str, value: NamespaceFile) -> None:
        ...

    def __setitem__(self, key: Any, value: Any):
        if isinstance(key, type):
            super().__setitem__(key, value)  # type: ignore
        else:
            self[type(value)][key] = value

    def __eq__(self, other: Any) -> bool:
        if self is other:
            return True
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

    def clear(self):
        self.extra.clear()
        super().clear()

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
        self,
        namespace: str,
        *extensions: str,
        extend: Optional[Any] = None,
    ) -> Iterator[Tuple[str, Any]]:
        """List and filter all the files in the namespace."""
        if extend and (origin := get_origin(extend)):
            extend = origin

        overlay = (
            ""
            if self.pack is None or self.pack.overlay_name is None
            else f"{self.pack.overlay_name}/"
        )

        for path, item in self.extra.items():
            if extensions and not any(path.endswith(ext) for ext in extensions):
                continue
            if extend and not isinstance(item, extend):
                continue
            yield f"{overlay}{self.directory}/{namespace}/{path}", item

        for content_type, container in self.items():
            if not container:
                continue
            if extensions and content_type.extension not in extensions:
                continue
            if extend and not issubclass(content_type, extend):
                continue
            prefix = "/".join((self.directory, namespace) + content_type.scope)
            for name, item in container.items():
                yield f"{overlay}{prefix}/{name}{content_type.extension}", item

    @classmethod
    def get_extra_info(cls) -> Dict[str, Type[PackFile]]:
        return {}

    @classmethod
    def scan(
        cls,
        prefix: str,
        origin: FileOrigin,
        filenames: List[PurePath],
        overlay_name: Optional[str] = None,
        extend_namespace: Iterable[Type[NamespaceFile]] = (),
        extend_namespace_extra: Optional[Mapping[str, Optional[Type[PackFile]]]] = None,
    ) -> Iterator[Tuple[str, "Namespace"]]:
        """Load namespaces by walking through a zipfile or directory."""
        preparts = tuple(filter(None, prefix.split("/")))
        if preparts and preparts[0] != (
            cls.directory if overlay_name is None else overlay_name
        ):
            return

        extra_info = cls.get_extra_info()
        if extend_namespace_extra:
            _update_with_none(extra_info, extend_namespace_extra)

        scope_map = dict(cls.scope_map)
        for file_type in extend_namespace:
            scope_map[file_type.scope, file_type.extension] = file_type

        name = None
        namespace = None

        for filename in filenames:
            parts = preparts + filename.parts

            if overlay_name is None:
                try:
                    directory, namespace_dir, *scope, basename = parts
                except ValueError:
                    continue
            else:
                try:
                    overlay, directory, namespace_dir, *scope, basename = parts
                except ValueError:
                    continue
                if overlay != overlay_name:
                    continue

            if directory != cls.directory:
                continue
            if name != namespace_dir:
                if name and namespace:
                    yield name, namespace
                name, namespace = namespace_dir, cls()

            assert name and namespace is not None
            extensions = list_extensions(PurePosixPath(basename))

            if file_type := extra_info.get(path := "/".join(scope + [basename])):
                namespace.extra[path] = file_type.load(origin, filename)
                continue

            file_dir: List[str] = []

            while True:
                path = tuple(scope)
                for extension in extensions:
                    if file_type := scope_map.get((path, extension)):
                        key = "/".join(
                            file_dir + [basename[: len(basename) - len(extension)]]
                        )
                        namespace[file_type][key] = file_type.load(origin, filename)
                        break
                else:
                    if scope:
                        file_dir.insert(0, scope.pop())
                        continue
                break

        if name and namespace:
            yield name, namespace

    def dump(self, namespace: str, origin: FileOrigin):
        """Write the namespace to a zipfile or to the filesystem."""
        _dump_files(origin, self.list_files(namespace))

    def __repr__(self) -> str:
        args = ", ".join(
            f"{self.field_map[key]}={value}"
            for key, value in self.items()
            if key in self.field_map and value
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

    def setdefault(
        self,
        key: str,
        default: Optional[NamespaceFileType] = None,
    ) -> NamespaceFileType:
        key1, key2 = self.split_key(key)
        return self.proxy[key1][self.proxy_key].setdefault(key2, default)  # type: ignore

    def merge(self, other: Mapping[Any, SupportsMerge]) -> bool:
        if isinstance(pack := self.proxy, Pack):
            return pack.merge_policy.merge_with_rules(
                pack=pack,
                current=self,  # type: ignore
                other=other,
                map_rules=lambda key: (
                    key,
                    pack.merge_policy.namespace.get(self.proxy_key, []),
                ),
            )
        return super().merge(other)

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


class Mcmeta(JsonFile):
    """Class representing a pack.mcmeta file."""

    def merge(self, other: "Mcmeta") -> bool:  # type: ignore
        for key, value in other.data.items():
            if key == "filter":
                block = self.data.setdefault("filter", {}).setdefault("block", [])
                for item in value.get("block", []):
                    if item not in block:
                        block.append(item)
            else:
                self.data[key] = value
        return True


class McmetaPin(Pin[str, PinType]):
    """Descriptor that makes it possible to bind pack.mcmeta information to attribute lookup."""

    def forward(self, obj: "Pack[Namespace]") -> JsonDict:
        return obj.mcmeta.data


class PackPin(McmetaPin[PinType]):
    """Descriptor that makes pack metadata accessible through attribute lookup."""

    def forward(self, obj: "Pack[Namespace]") -> JsonDict:
        return super().forward(obj).setdefault("pack", {})


class OverlayContainer(MatchMixin, MergeMixin, Container[str, PackType]):
    """Container that stores overlays."""

    pack: Optional[PackType] = None

    __currently_merging: Optional[Any] = Any

    def process(self, key: str, value: PackType) -> PackType:
        supported_formats = value.supported_formats

        value.overlay_name = key
        value.overlay_parent = self.pack
        self.merge(value.overlays)
        value.overlays = self

        if self.pack is not None:
            value.configure(self.pack)

        value.extend_extra["pack.mcmeta"] = None
        value.extend_extra["pack.png"] = None

        if supported_formats is not None:
            value.supported_formats = supported_formats

        return value

    def bind(self, pack: PackType):
        """Handle insertion."""
        self.pack = pack

        for key, value in self.items():
            try:
                self.process(key, value)
            except Drop:
                del self[key]

    def __delitem__(self, key: str):
        super().__delitem__(key)
        if self.pack is not None:
            overlays: Any = self.pack.mcmeta.data.get("overlays", {})
            entries = overlays.get("entries", [])
            for i, entry in enumerate(entries):
                if entry.get("directory") == key:
                    del entries[i]

    def missing(self, key: str) -> PackType:
        if self.pack is None:
            raise ValueError("Unbound overlay container.")
        return type(self.pack)()

    def setdefault(
        self,
        key: str,
        default: Optional[PackType] = None,
        *,
        supported_formats: Optional[SupportedFormats] = None,
    ) -> PackType:
        value = self._wrapped.get(key)
        if value is not None:
            return value
        if default is None:
            default = self.missing(key)
        if supported_formats is not None:
            default.supported_formats = supported_formats
        self[key] = default
        return default

    def merge(self, other: Mapping[str, SupportsMerge]) -> bool:
        previous_other = self.__currently_merging
        if previous_other is other:
            return True
        self.__currently_merging = other
        try:
            return super().merge(other)
        finally:
            self.__currently_merging = previous_other

    def __eq__(self, other: Any) -> bool:
        if self is other:
            return True
        if isinstance(other, Mapping):
            rhs: Mapping[str, PackType] = other
            return (
                all(not self[k] for k in self.keys() - rhs.keys())
                and all(not rhs[k] for k in rhs.keys() - self.keys())
                and all(self[k] == rhs[k] for k in self.keys() & rhs.keys())
            )
        return NotImplemented

    def __bool__(self) -> bool:
        return any(self.values())


class UnveilMapping(Mapping[str, FileSystemPath]):
    """Unveil mapping."""

    files: Mapping[str, FileSystemPath]
    prefix: str

    def __init__(self, files: Mapping[str, FileSystemPath], prefix: str = ""):
        self.files = files
        self.prefix = prefix

    def with_prefix(self, prefix: str) -> "UnveilMapping":
        return self.__class__(self.files, prefix)

    def __getitem__(self, key: str) -> FileSystemPath:
        sep = "/" if key and self.prefix else ""
        return self.files[f"{self.prefix}{sep}{key}"]

    def __iter__(self) -> Iterator[str]:
        if self.prefix:
            directory_prefix = f"{self.prefix}/"
            for key in self.files:
                if key == self.prefix:
                    yield ""
                elif key.startswith(directory_prefix):
                    yield key[len(directory_prefix) :]
        else:
            yield from self.files

    def __len__(self) -> int:
        return len(self.files)

    def __eq__(self, other: Any) -> bool:
        return self is other

    def __hash__(self) -> int:
        return id(self)

    def __repr__(self) -> str:
        args = f"files={self.files}"
        if self.prefix:
            args += f"prefix={self.prefix!r}"
        return f"{self.__class__.__name__}({args})"


class PackOverwrite(Exception):
    """Raised when trying to overwrite a pack."""

    path: FileSystemPath

    def __init__(self, path: FileSystemPath) -> None:
        super().__init__(path)
        self.path = path

    def __str__(self) -> str:
        return f'Couldn\'t overwrite "{str(self.path)}".'


class Pack(MatchMixin, MergeMixin, Container[str, NamespaceType]):
    """Class representing a pack."""

    name: Optional[str]
    path: Optional[Path]
    zipped: bool
    compression: Optional[Literal["none", "deflate", "bzip2", "lzma"]]
    compression_level: Optional[int]

    extra: PackExtraContainer["Pack[NamespaceType]"]
    mcmeta: ExtraPin[Mcmeta] = ExtraPin("pack.mcmeta", default_factory=lambda: Mcmeta())
    icon: ExtraPin[Optional[PngFile]] = ExtraPin("pack.png", default=None)

    description: PackPin[TextComponent] = PackPin("description", default="")
    pack_format: PackPin[int] = PackPin("pack_format", default=0)
    filter: McmetaPin[JsonDict] = McmetaPin(
        "filter", default_factory=lambda: {"block": []}
    )

    overlay_name: Optional[str]
    overlay_parent: Optional[Self]
    overlays: OverlayContainer[Self]

    extend_extra: Dict[str, Optional[Type[PackFile]]]
    extend_namespace: List[Type[NamespaceFile]]
    extend_namespace_extra: Dict[str, Optional[Type[PackFile]]]

    merge_policy: MergePolicy
    unveiled: Dict[Union[Path, UnveilMapping], Set[str]]

    namespace_type: ClassVar[Type[Namespace]]
    default_name: ClassVar[str]
    pack_format_registry: ClassVar[Dict[Tuple[int, ...], int]]
    latest_pack_format: ClassVar[int]

    def __init_subclass__(cls):
        cls.namespace_type = get_args(getattr(cls, "__orig_bases__")[0])[0]

    def __init__(
        self,
        name: Optional[str] = None,
        path: Optional[FileSystemPath] = None,
        zipfile: Optional[ZipFile] = None,
        mapping: Optional[Mapping[str, FileSystemPath]] = None,
        zipped: bool = False,
        compression: Optional[Literal["none", "deflate", "bzip2", "lzma"]] = None,
        compression_level: Optional[int] = None,
        mcmeta: Optional[Mcmeta] = None,
        icon: Optional[PngFile] = None,
        description: Optional[str] = None,
        pack_format: Optional[int] = None,
        supported_formats: Optional[SupportedFormats] = None,
        filter: Optional[JsonDict] = None,
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

        self.overlay_name = None
        self.overlay_parent = None
        self.overlays = OverlayContainer()
        self.overlays.bind(self)

        self.extend_extra = dict(extend_extra or {})
        self.extend_namespace = list(extend_namespace)
        self.extend_namespace_extra = dict(extend_namespace_extra or {})

        self.merge_policy = MergePolicy()
        if merge_policy:
            self.merge_policy.extend(merge_policy)

        self.unveiled = {}

        if mcmeta is not None:
            self.mcmeta = mcmeta
        if icon is not None:
            self.icon = icon
        if description is not None:
            self.description = description
        if pack_format is not None:
            self.pack_format = pack_format
        if supported_formats is not None:
            self.supported_formats = supported_formats
        if filter is not None:
            self.filter = filter

        self.load(path or zipfile or mapping)

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
        if other is not None:
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
    def __setitem__(self, key: str, value: NamespaceType) -> None:
        ...

    @overload
    def __setitem__(self, key: str, value: NamespaceFile) -> None:
        ...

    def __setitem__(self, key: str, value: Any):
        if isinstance(value, Namespace):
            super().__setitem__(key, value)  # type: ignore
        else:
            NamespaceProxy[NamespaceFile](self, type(value))[key] = value

    def __eq__(self, other: Any) -> bool:
        if self is other:
            return True
        if type(self) == type(other) and not (
            self.name == other.name
            and self.extra == other.extra
            and (
                self.overlay_parent is not None
                or other.overlay_parent is not None
                or self.overlays == other.overlays
            )
        ):
            return False
        if isinstance(other, Mapping):
            rhs: Mapping[str, Namespace] = other
            return all(self[key] == rhs[key] for key in self.keys() | rhs.keys())
        return NotImplemented

    def __hash__(self) -> int:
        return id(self)

    def __bool__(self) -> bool:
        return (
            any(self.values())
            or self.extra.keys() > {"pack.mcmeta"}
            or (self.overlay_parent is None and bool(self.overlays))
        )

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
            self.overlays.merge(other.overlays)  # type: ignore

        empty_namespaces = [key for key, value in self.items() if not value]  # type: ignore
        for namespace in empty_namespaces:
            del self[namespace]  # type: ignore

        return True

    @property
    def content(self) -> Iterator[Tuple[str, NamespaceFile]]:
        """Iterator that yields all the files stored in the pack."""
        for file_type in self.resolve_scope_map().values():
            yield from NamespaceProxy[NamespaceFile](self, file_type).items()

    def clear(self):
        self.extra.clear()
        super().clear()
        if not self.pack_format:
            self.pack_format = self.latest_pack_format
        if not self.description:
            self.description = ""

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

        overlay = "" if self.overlay_name is None else f"{self.overlay_name}/"

        for path, item in self.extra.items():
            if extensions and not any(path.endswith(ext) for ext in extensions):
                continue
            if extend and not isinstance(item, extend):
                continue
            if overlay and path in ("pack.mcmeta", "pack.png"):
                continue
            yield f"{overlay}{path}", item

        for namespace_name, namespace in self.items():
            yield from namespace.list_files(namespace_name, *extensions, extend=extend)  # type: ignore

        if self.overlay_parent is None:
            for overlay in self.overlays.values():
                yield from overlay.list_files(*extensions, extend=extend)  # type: ignore

    @property
    def supported_formats(self) -> Optional[SupportedFormats]:
        if self.overlay_parent is not None:
            overlays: Any = self.overlay_parent.mcmeta.data.get("overlays", {})
            for entry in overlays.get("entries", []):
                if entry.get("directory") == self.overlay_name:
                    return entry.get("formats")
        else:
            return self.mcmeta.data.get("pack", {}).get("supported_formats")

    @supported_formats.setter
    def supported_formats(self, value: SupportedFormats):
        if self.overlay_parent is not None:
            overlays: Any = self.overlay_parent.mcmeta.data.setdefault("overlays", {})
            for entry in overlays.setdefault("entries", []):
                if entry.get("directory") == self.overlay_name:
                    entry["formats"] = value
                    break
            else:
                overlays["entries"].append(
                    {"formats": value, "directory": self.overlay_name}
                )
        else:
            self.mcmeta.data.setdefault("pack", {})["supported_formats"] = value

    @classmethod
    def get_extra_info(cls) -> Dict[str, Type[PackFile]]:
        return {"pack.mcmeta": Mcmeta, "pack.png": PngFile}

    def resolve_extra_info(self) -> Dict[str, Type[PackFile]]:
        extra_info = self.get_extra_info()
        if self.extend_extra:
            _update_with_none(extra_info, self.extend_extra)
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
            _update_with_none(namespace_extra_info, self.extend_namespace_extra)
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

        if origin and not isinstance(origin, Mapping):
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
            self.mount("", origin)

        if not self.pack_format:
            self.pack_format = self.latest_pack_format
        if not self.description:
            self.description = ""

    def mount(
        self,
        prefix: str,
        origin: FileOrigin,
        origin_folders: Optional[Dict[str, List[PurePath]]] = None,
    ):
        """Mount files from a zipfile or from the filesystem."""
        files: Dict[str, PackFile] = {}

        for expected_filename, file_type in self.resolve_extra_info().items():
            filename = (
                expected_filename
                if self.overlay_name is None
                else f"{self.overlay_name}/{expected_filename}"
            )
            if not prefix:
                if loaded := file_type.try_load(origin, filename):
                    files[expected_filename] = loaded
            elif prefix == filename:
                if loaded := file_type.try_load(origin, ""):
                    files[expected_filename] = loaded
            elif filename.startswith(prefix + "/"):
                if loaded := file_type.try_load(origin, filename[len(prefix) + 1 :]):
                    files[expected_filename] = loaded

        self.extra.merge(files)

        if origin_folders is None:
            origin_folders = list_origin_folders(prefix, origin)

        scan_folder = (
            self.namespace_type.directory
            if self.overlay_name is None
            else self.overlay_name
        )

        namespaces = {
            name: namespace
            for name, namespace in self.namespace_type.scan(
                prefix,
                origin,
                origin_folders.pop(scan_folder, []),
                self.overlay_name,
                self.extend_namespace,
                self.extend_namespace_extra,
            )
        }

        self.merge(namespaces)  # type: ignore

        if self.overlay_parent is None:
            overlays: Any = self.mcmeta.data.get("overlays", {})
            for entry in overlays.get("entries", []):
                name = entry.get("directory")
                if name is not None:
                    self.overlays[name].mount(prefix, origin, origin_folders)

            remaining_overlays = list(origin_folders)
            for name in remaining_overlays:
                overlay = self.overlays[name]
                overlay.mount(prefix, origin, origin_folders)
                if not overlay:
                    del self.overlays[name]

    def unveil(self, prefix: str, origin: Union[FileSystemPath, UnveilMapping]):
        """Lazily mount resources from the root of a pack on the filesystem."""
        if not isinstance(origin, UnveilMapping):
            origin = Path(origin).resolve()

        mounted = self.unveiled.setdefault(origin, set())

        if prefix in mounted:
            return

        to_remove: Set[str] = set()
        for mnt in mounted:
            if prefix.startswith(mnt):
                return
            if mnt.startswith(prefix):
                to_remove.add(mnt)

        mounted -= to_remove
        mounted.add(prefix)

        if isinstance(origin, UnveilMapping):
            self.mount(prefix, origin.with_prefix(prefix))
        else:
            self.mount(prefix, origin / prefix)

    def dump(self, origin: FileOrigin):
        """Write the content of the pack to a zipfile or to the filesystem"""
        _dump_files(origin, self.list_files())

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
                raise PackOverwrite(output_path)
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


def _dump_files(origin: FileOrigin, files: Iterable[Tuple[str, PackFile]]):
    dirs: DefaultDict[Tuple[str, ...], List[Tuple[str, PackFile]]] = defaultdict(list)

    for full_path, item in files:
        directory, _, filename = full_path.rpartition("/")
        dirs[(directory,) if directory else ()].append((filename, item))

    for directory, entries in dirs.items():
        if not isinstance(origin, (ZipFile, Mapping)):
            Path(origin, *directory).resolve().mkdir(parents=True, exist_ok=True)
        for filename, f in entries:
            f.dump(origin, "/".join(directory + (filename,)))


K = TypeVar("K")
V = TypeVar("V")


def _update_with_none(dst: MutableMapping[K, V], src: Mapping[K, Optional[V]]):
    for k, v in list(src.items()):
        if v is None:
            dst.pop(k, None)
        else:
            dst[k] = v
