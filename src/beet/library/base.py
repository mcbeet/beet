__all__ = [
    "LATEST_MINECRAFT_VERSION",
    "PACK_COMPRESSION",
    "ExtraContainer",
    "ExtraPin",
    "Mcmeta",
    "McmetaPin",
    "MergeCallback",
    "MergePolicy",
    "Namespace",
    "NamespaceContainer",
    "NamespaceExtraContainer",
    "NamespaceFile",
    "NamespaceFileScope",
    "NamespacePin",
    "NamespaceProxy",
    "NamespaceProxyDescriptor",
    "OverlayContainer",
    "Pack",
    "PackExtraContainer",
    "PackFile",
    "PackOverwrite",
    "PackPin",
    "SupportsExtra",
    "UnveilMapping",
    "create_group_map",
    "get_output_scope",
    "list_input_scopes",
]


import shutil
from collections import defaultdict
from collections.abc import (
    Callable,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    Sequence,
)
from contextlib import nullcontext
from copy import deepcopy
from dataclasses import dataclass, field
from functools import partial
from itertools import count
from pathlib import Path, PurePath, PurePosixPath
from types import get_original_bases
from typing import (
    Any,
    ClassVar,
    Generic,
    Literal,
    Protocol,
    Self,
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
from beet.core.utils import (
    FileSystemPath,
    JsonDict,
    SupportedFormats,
    TextComponent,
)
from beet.resources.pack_format_registry import PackFormatRegistryContainer
from beet.toolchain.config import FormatSpecifier

from .utils import list_extensions, list_origin_folders

LATEST_MINECRAFT_VERSION: str = "26.3"


T = TypeVar("T")
PinType = TypeVar("PinType", covariant=True)
PackFileType = TypeVar("PackFileType", bound="PackFile")
NamespaceType = TypeVar("NamespaceType", bound="Namespace")
NamespaceFileType = TypeVar("NamespaceFileType", bound="NamespaceFile")
PackType = TypeVar("PackType", bound="Pack[Any]")
MergeableType = TypeVar("MergeableType", bound=SupportsMerge)

type PackFile = File[Any, Any]


PACK_COMPRESSION: dict[str, int] = {
    "none": ZIP_STORED,
    "deflate": ZIP_DEFLATED,
    "bzip2": ZIP_BZIP2,
    "lzma": ZIP_LZMA,
}

type NamespaceFileScope = tuple[str, ...] | Mapping[int, tuple[str, ...]]


class NamespaceFile(Protocol):
    """Protocol for detecting files that belong in pack namespaces."""

    scope: ClassVar[NamespaceFileScope]
    extension: ClassVar[str]

    snake_name: ClassVar[str]

    def __init__(
        self,
        _content: Any | None = None,
        /,
        *,
        source_path: FileSystemPath | None = None,
        source_start: int | None = None,
        source_stop: int | None = None,
        on_bind: Callable[[Any, Any, str], Any] | None = None,
        original: Any = None,
    ) -> None: ...

    def merge(self, other: Any) -> bool: ...

    def bind(self, pack: Any, path: str): ...

    def set_content(self, content: Any): ...

    def get_content(self) -> Any: ...

    def ensure_source_path(self) -> FileSystemPath: ...

    def ensure_serialized(
        self,
        serializer: Callable[[Any], Any] | None = None,
    ) -> Any: ...

    def ensure_deserialized(
        self,
        deserializer: Callable[[Any], Any] | None = None,
    ) -> Any: ...

    @classmethod
    def default(cls) -> Any: ...

    def copy(self) -> Self: ...

    @classmethod
    def load(cls, origin: FileOrigin, path: FileSystemPath) -> Self: ...

    def dump(self, origin: FileOrigin, path: FileSystemPath): ...

    def convert(self, file_type: type[PackFileType]) -> PackFileType: ...


class MergeCallback(Protocol):
    """Protocol for detecting merge callbacks."""

    def __call__(
        self, pack: Any, path: str, current: Any, conflict: Any, /
    ) -> bool: ...


@dataclass
class MergePolicy:
    """Class holding lists of rules for merging files."""

    extra: dict[str, list[MergeCallback]] = field(default_factory=dict)
    namespace: dict[type[NamespaceFile], list[MergeCallback]] = field(
        default_factory=dict
    )
    namespace_extra: dict[str, list[MergeCallback]] = field(default_factory=dict)

    def extend(self, other: MergePolicy):
        for rules, other_rules in [
            (self.extra, other.extra),
            (self.namespace, other.namespace),
            (self.namespace_extra, other.namespace_extra),
        ]:
            for key, value in other_rules.items():
                rules.setdefault(key, []).extend(value)  # pyright: ignore[reportArgumentType]

    def extend_extra(self, filename: str, rule: MergeCallback):
        """Add rule for merging extra files."""
        self.extra.setdefault(filename, []).append(rule)

    def extend_namespace(self, file_type: type[NamespaceFile], rule: MergeCallback):
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
        map_rules: Callable[[str], tuple[str, list[MergeCallback]]],
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

    namespace: NamespaceType | None = None

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
                current=self,  # pyright: ignore[reportArgumentType]
                other=other,
                map_rules=lambda key: (
                    f"{name}:{key}",
                    pack.merge_policy.namespace_extra.get(key, []),
                ),
            )
        return super().merge(other)


class PackExtraContainer(ExtraContainer, Generic[PackType]):
    """Pack extra container."""

    pack: PackType | None = None

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
                current=self,  # pyright: ignore[reportArgumentType]
                other=other,
                map_rules=lambda key: (
                    key,
                    pack.merge_policy.extra.get(key, []),
                ),
            )
        return super().merge(other)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Mapping):
            return False

        left, right = dict(self), dict(other)

        left_mcmeta = left.pop("pack.mcmeta", None)
        right_mcmeta = right.pop("pack.mcmeta", None)

        if left != right:
            return False

        if left_mcmeta != right_mcmeta:
            if self.pack is not None and (left_mcmeta is None or right_mcmeta is None):
                default_mcmeta = type(self.pack)().mcmeta
                return left_mcmeta == default_mcmeta or right_mcmeta == default_mcmeta
            return False

        return True


class NamespaceContainer(MatchMixin, MergeMixin, Container[str, NamespaceFileType]):
    """Container that stores one type of files in a namespace."""

    namespace: Namespace | None = None
    file_type: type[NamespaceFileType] | None = None

    def process(self, key: str, value: NamespaceFileType) -> NamespaceFileType:
        if (
            self.namespace is not None
            and self.namespace.pack is not None
            and self.namespace.name
        ):
            value.bind(self.namespace.pack, f"{self.namespace.name}:{key}")
        return value

    def bind(self, namespace: Namespace, file_type: type[NamespaceFileType]):
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
        default: NamespaceFileType | None = None,
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
                current=self,  # pyright: ignore[reportArgumentType]
                other=other,
                map_rules=lambda key: (
                    f"{name}:{key}",
                    pack.merge_policy.namespace.get(file_type, []),
                ),
            )
        return super().merge(other)

    def generate_tree(self, path: str = "") -> dict[Any, Any]:
        """Generate a hierarchy of nested dictionaries representing the files and folders."""
        prefix = path.split("/") if path else []
        tree: dict[Any, Any] = {}

        for filename, file_instance in self.items():
            parts = filename.split("/")

            if parts[: len(prefix)] != prefix:
                continue

            parent = tree
            for part in parts[len(prefix) :]:
                parent = parent.setdefault(part, {})

            parent[self.file_type] = file_instance

        return tree


class NamespacePin(Pin[type[NamespaceFileType], NamespaceContainer[NamespaceFileType]]):
    """Descriptor for accessing namespace containers by attribute lookup."""


class Namespace(
    MergeMixin,
    Container[type[NamespaceFile], NamespaceContainer[NamespaceFile]],
):
    """Class representing a namespace."""

    pack: Pack[Namespace] | None = None
    name: str | None = None
    extra: NamespaceExtraContainer[Namespace]

    directory: ClassVar[str]
    field_map: ClassVar[Mapping[type[NamespaceFile], str]]
    scope_map: ClassVar[Mapping[tuple[tuple[str, ...], str], type[NamespaceFile]]]

    def __init_subclass__(cls):
        pins = NamespacePin[NamespaceFile].collect_from(cls)
        cls.field_map = {pin.key: attr for attr, pin in pins.items()}
        cls.scope_map = {
            (scope, pin.key.extension): pin.key
            for pin in pins.values()
            for scope in list_input_scopes(pin.key.scope)
        }

    def __init__(self):
        super().__init__()
        self.extra = NamespaceExtraContainer()

    def process(
        self,
        key: type[NamespaceFile],
        value: NamespaceContainer[NamespaceFile],
    ) -> NamespaceContainer[NamespaceFile]:
        value.bind(self, key)
        return value

    def bind(self, pack: Pack[Namespace], name: str):
        """Handle insertion."""
        self.pack = pack
        self.name = name

        for key, value in self.items():
            self.process(key, value)

        self.extra.bind(self)

    @overload
    def __setitem__(
        self,
        key: type[NamespaceFile],
        value: NamespaceContainer[NamespaceFile],
    ) -> None: ...

    @overload
    def __setitem__(self, key: str, value: NamespaceFile) -> None: ...

    def __setitem__(self, key: Any, value: Any):
        if isinstance(key, type):
            super().__setitem__(key, value)
        else:
            self[type(value)][key] = value

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        if (
            isinstance(other, Namespace)
            and type(self) is type(other)
            and not self.extra == other.extra
        ):
            return False
        if isinstance(other, Mapping):
            rhs: Mapping[type[NamespaceFile], NamespaceContainer[NamespaceFile]] = other  # pyright: ignore[reportAssignmentType]
            return all(
                self[key] == rhs.get(key, {}) for key in self.keys() | rhs.keys()
            )
        return NotImplemented

    def __bool__(self) -> bool:
        return any(self.values()) or bool(self.extra)

    def missing(self, key: type[NamespaceFile]) -> NamespaceContainer[NamespaceFile]:
        return NamespaceContainer()

    def merge(
        self: MutableMapping[T, MergeableType],
        other: Mapping[T, MergeableType],
    ) -> bool:
        super().merge(other)  # pyright: ignore[reportAttributeAccessIssue]

        if isinstance(self, Namespace) and isinstance(other, Namespace):
            self.extra.merge(other.extra)

        empty_containers = [key for key, value in self.items() if not value]
        for container in empty_containers:
            del self[container]  # pyright: ignore[reportArgumentType]

        return True

    def clear(self):
        self.extra.clear()
        super().clear()

    @property
    def content(self) -> Iterator[tuple[str, NamespaceFile]]:
        """Iterator that yields all the files stored in the namespace."""
        for container in self.values():
            yield from container.items()

    @overload
    def list_files(
        self,
        namespace: str,
        *extensions: str,
    ) -> Iterator[tuple[str, PackFile]]: ...

    @overload
    def list_files(
        self,
        namespace: str,
        *extensions: str,
        extend: type[T],
    ) -> Iterator[tuple[str, T]]: ...

    def list_files(
        self,
        namespace: str,
        *extensions: str,
        extend: Any | None = None,
    ) -> Iterator[tuple[str, Any]]:
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

            scope = get_output_scope(content_type.scope, self.pack)
            prefix = "/".join((self.directory, namespace) + scope)
            for name, item in container.items():
                yield f"{overlay}{prefix}/{name}{content_type.extension}", item

    @classmethod
    def get_extra_info(cls) -> dict[str, type[PackFile]]:
        return {}

    @classmethod
    def scan(
        cls,
        prefix: str,
        origin: FileOrigin,
        filenames: list[PurePath],
        overlay_name: str | None = None,
        extend_namespace: Iterable[type[NamespaceFile]] = (),
        extend_namespace_extra: Mapping[str, type[PackFile] | None] | None = None,
    ) -> Iterator[tuple[str, Namespace]]:
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
            for scope in list_input_scopes(file_type.scope):
                scope_map[scope, file_type.extension] = file_type

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

            file_dir: list[str] = []

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
    ContainerProxy[type[NamespaceFileType], str, NamespaceFileType],
):
    """Aggregated view that exposes a certain type of files over all namespaces."""

    def split_key(self, key: str) -> tuple[str, str]:
        namespace, _, file_path = key.partition(":")
        return namespace, file_path

    def join_key(self, key1: str, key2: str) -> str:
        return f"{key1}:{key2}"

    def setdefault(
        self,
        key: str,
        default: NamespaceFileType | None = None,
    ) -> NamespaceFileType:
        key1, key2 = self.split_key(key)
        return self.proxy[key1][self.proxy_key].setdefault(key2, default)  # pyright: ignore[reportArgumentType]

    def merge(self, other: Mapping[Any, SupportsMerge]) -> bool:
        if isinstance(pack := self.proxy, Pack):
            return pack.merge_policy.merge_with_rules(
                pack=pack,
                current=self,  # pyright: ignore[reportArgumentType]
                other=other,
                map_rules=lambda key: (
                    key,
                    pack.merge_policy.namespace.get(self.proxy_key, []),
                ),
            )
        return super().merge(other)

    def walk(self) -> Iterator[tuple[str, set[str], dict[str, NamespaceFileType]]]:
        """Walk over the file hierarchy."""
        for prefix, namespace in self.proxy.items():
            separator = ":"
            roots: list[tuple[str, dict[Any, Any]]] = [
                (prefix, namespace[self.proxy_key].generate_tree())  # pyright: ignore[reportAttributeAccessIssue]
            ]

            while roots:
                prefix, root = roots.pop()

                dirs: set[str] = set()
                files: dict[str, NamespaceFileType] = {}

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

    proxy_key: type[NamespaceFileType]

    def __get__(
        self, obj: Any, objtype: type[Any] | None = None
    ) -> NamespaceProxy[NamespaceFileType]:
        return NamespaceProxy[NamespaceFileType](obj, self.proxy_key)


class Mcmeta(JsonFile):
    """Class representing a pack.mcmeta file."""

    def merge(self, other: Mcmeta) -> bool:  # pyright: ignore[reportIncompatibleMethodOverride]
        for key, value in other.data.items():
            if key == "filter":
                block = self.data.setdefault("filter", {}).setdefault("block", [])
                for item in value.get("block", []):
                    if item not in block:
                        block.append(item)
            elif key == "overlays":
                for other_entry in value.get("entries"):
                    overlays: Any = self.data.setdefault("overlays", {})
                    for entry in overlays.setdefault("entries", []):
                        if entry.get("directory") == other_entry.get("directory"):
                            if (value := deepcopy(other_entry.get("formats"))) is None:
                                entry.pop("formats", None)
                            else:
                                entry["formats"] = value
                            if (
                                value := deepcopy(other_entry.get("min_format"))
                            ) is None:
                                entry.pop("min_format", None)
                            else:
                                entry["min_format"] = value
                            if (
                                value := deepcopy(other_entry.get("max_format"))
                            ) is None:
                                entry.pop("max_format", None)
                            else:
                                entry["max_format"] = value
                            break
                    else:
                        overlays["entries"].append(deepcopy(other_entry))
            else:
                self.data[key] = value
        return True


class McmetaPin(Pin[str, PinType]):
    """Descriptor that makes it possible to bind pack.mcmeta information to attribute lookup."""

    def forward(self, obj: Pack[Namespace]) -> JsonDict:
        return obj.mcmeta.data


class PackPin(McmetaPin[PinType]):
    """Descriptor that makes pack metadata accessible through attribute lookup."""

    def forward(self, obj: Pack[Namespace]) -> JsonDict:
        return super().forward(obj).setdefault("pack", {})


class OverlayContainer(MatchMixin, MergeMixin, Container[str, PackType]):
    """Container that stores overlays."""

    pack: PackType | None = None

    __currently_merging: Any | None = Any

    def process(self, key: str, value: PackType) -> PackType:
        supported_formats = value.supported_formats
        min_format = value.min_format
        max_format = value.max_format
        description = value.description

        value.overlay_name = key
        value.overlay_parent = self.pack
        self.merge(value.overlays)
        value.overlays = self

        if self.pack is not None:
            value.configure(self.pack)

        value.extend_extra["pack.mcmeta"] = None
        value.extend_extra["pack.png"] = None

        if "pack.mcmeta" in value.extra:
            del value.extra["pack.mcmeta"]
        if "pack.png" in value.extra:
            del value.extra["pack.png"]

        if supported_formats is not None:
            value.supported_formats = supported_formats
        if min_format is not None:
            value.min_format = min_format
        if max_format is not None:
            value.max_format = max_format
        value.description = description

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
        orphan = self[key]
        orphan.overlay_name = None
        orphan.overlay_parent = None
        super().__delitem__(key)
        if self.pack is not None:
            overlays: Any = self.pack.mcmeta.data.get("overlays", {})
            entries = overlays.get("entries", [])
            for i, entry in enumerate(entries):
                if entry.get("directory") == key:
                    del entries[i]
                    if not entries:
                        del overlays["entries"]
                        if not overlays:
                            del self.pack.mcmeta.data["overlays"]
                    break

    def missing(self, key: str) -> PackType:
        if self.pack is None:
            raise ValueError("Unbound overlay container.")
        return type(self.pack)()

    def setdefault(
        self,
        key: str,
        default: PackType | None = None,
        *,
        supported_formats: SupportedFormats | None = None,
        min_format: FormatSpecifier | None = None,
        max_format: FormatSpecifier | None = None,
    ) -> PackType:
        value = self._wrapped.get(key)
        if value is not None:
            return value
        if default is None:
            default = self.missing(key)
        if supported_formats is not None:
            default.supported_formats = supported_formats
            default.min_format = None
            default.max_format = None
        if min_format is not None:
            default.min_format = min_format
        if max_format is not None:
            default.max_format = max_format
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

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        if isinstance(other, Mapping):
            rhs: Mapping[str, PackType] = other  # pyright: ignore[reportAssignmentType]
            return (
                all(not self[k] for k in self.keys() - rhs.keys())
                and all(not rhs[k] for k in rhs.keys() - self.keys())
                and all(self[k] == rhs[k] for k in self.keys() & rhs.keys())
            )
        return NotImplemented

    def __bool__(self) -> bool:
        return any(self.values())

    def cleanup(self, directories: Iterable[str] | None = None):
        """Remove empty overlays."""
        if directories is None:
            directories = list(self)
        for directory in directories:
            if not self[directory]:
                del self[directory]


class UnveilMapping(Mapping[str, FileSystemPath]):
    """Unveil mapping."""

    files: Mapping[str, FileSystemPath]
    prefix: str

    def __init__(self, files: Mapping[str, FileSystemPath], prefix: str = ""):
        self.files = files
        self.prefix = prefix

    def with_prefix(self, prefix: str) -> UnveilMapping:
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

    def __eq__(self, other: object) -> bool:
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
        return f'Couldn\'t overwrite "{self.path!s}".'


class Pack(MatchMixin, MergeMixin, Container[str, NamespaceType]):
    """Class representing a pack."""

    name: str | None
    path: Path | None
    zipped: bool
    compression: Literal["none", "deflate", "bzip2", "lzma"] | None
    compression_level: int | None

    extra: PackExtraContainer[Pack[NamespaceType]]
    mcmeta: ExtraPin[Mcmeta] = ExtraPin("pack.mcmeta", default_factory=lambda: Mcmeta())
    icon: ExtraPin[PngFile | None] = ExtraPin("pack.png", default=None)

    description: PackPin[TextComponent] = PackPin("description", default="")
    pack_format: PackPin[int | None] = PackPin(
        "pack_format", default=None, delete_default=True
    )
    filter: McmetaPin[JsonDict] = McmetaPin(
        "filter", default_factory=lambda: {"block": []}
    )

    overlay_name: str | None
    overlay_parent: Self | None
    overlays: OverlayContainer[Self]

    extend_extra: dict[str, type[PackFile] | None]
    extend_namespace: list[type[NamespaceFile]]
    extend_namespace_extra: dict[str, type[PackFile] | None]

    merge_policy: MergePolicy
    unveiled: dict[Path | UnveilMapping, set[str]]

    namespace_type: ClassVar[type[Namespace]]
    default_name: ClassVar[str]
    pack_format_registry: ClassVar[PackFormatRegistryContainer]
    latest_pack_format: ClassVar[int | FormatSpecifier]
    pack_format_switch_format: ClassVar[int]

    def __init_subclass__(cls):
        if not hasattr(cls, "namespace_type"):
            cls.namespace_type = get_args(get_original_bases(cls)[0])[0]

    def __init__(
        self,
        name: str | None = None,
        path: FileSystemPath | None = None,
        zipfile: ZipFile | None = None,
        mapping: Mapping[str, FileSystemPath] | None = None,
        zipped: bool = False,
        compression: Literal["none", "deflate", "bzip2", "lzma"] | None = None,
        compression_level: int | None = None,
        mcmeta: Mcmeta | None = None,
        icon: PngFile | None = None,
        description: str | None = None,
        pack_format: int | None = None,
        supported_formats: SupportedFormats | None = None,
        min_format: FormatSpecifier | None = None,
        max_format: FormatSpecifier | None = None,
        filter: JsonDict | None = None,
        extend_extra: Mapping[str, type[PackFile]] | None = None,
        extend_namespace: Iterable[type[NamespaceFile]] = (),
        extend_namespace_extra: Mapping[str, type[PackFile]] | None = None,
        merge_policy: MergePolicy | None = None,
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
        if min_format is not None:
            self.min_format = min_format
        if max_format is not None:
            self.max_format = max_format
        if filter is not None:
            self.filter = filter

        self.load(path or zipfile or mapping)

    def configure(
        self,
        other: Self | None = None,
        *,
        extend_extra: Mapping[str, type[PackFile]] | None = None,
        extend_namespace: Iterable[type[NamespaceFile]] = (),
        extend_namespace_extra: Mapping[str, type[PackFile]] | None = None,
        merge_policy: MergePolicy | None = None,
    ) -> Self:
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
    def __getitem__(self, key: str) -> NamespaceType: ...

    @overload
    def __getitem__(
        self, key: type[NamespaceFileType]
    ) -> NamespaceProxy[NamespaceFileType]: ...

    def __getitem__(self, key: Any) -> Any:
        if isinstance(key, str):
            return super().__getitem__(key)
        return NamespaceProxy(self, key)

    @overload
    def __setitem__(self, key: str, value: NamespaceType) -> None: ...

    @overload
    def __setitem__(self, key: str, value: NamespaceFile) -> None: ...

    def __setitem__(self, key: str, value: Any):
        if isinstance(value, Namespace):
            super().__setitem__(key, value)  # pyright: ignore[reportArgumentType]
        else:
            NamespaceProxy[NamespaceFile](self, type(value))[key] = value

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        if (
            isinstance(other, Pack)
            and type(self) is type(other)
            and not (
                self.name == other.name
                and self.extra == other.extra
                and (
                    self.overlay_parent is not None
                    or other.overlay_parent is not None
                    or self.overlays == other.overlays
                )
            )
        ):
            return False
        if isinstance(other, Mapping):
            rhs: Mapping[str, Namespace] = other  # pyright: ignore[reportAssignmentType]
            return all(
                self[key] == rhs.get(key, {}) for key in self.keys() | rhs.keys()
            )
        return NotImplemented

    def __hash__(self) -> int:
        return id(self)

    def __bool__(self) -> bool:
        return (
            any(self.values())
            or self.extra.keys() > {"pack.mcmeta"}
            or (self.overlay_parent is None and bool(self.overlays))
        )

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_):
        self.save(overwrite=True)

    def process(self, key: str, value: NamespaceType) -> NamespaceType:
        value.bind(self, key)  # pyright: ignore[reportArgumentType]
        return value

    def missing(self, key: str) -> NamespaceType:
        return self.namespace_type()  # pyright: ignore[reportReturnType]

    def merge(
        self: MutableMapping[T, MergeableType], other: Mapping[T, MergeableType]
    ) -> bool:
        super().merge(other)  # pyright: ignore[reportAttributeAccessIssue]

        if isinstance(self, Pack) and isinstance(other, Pack):
            self.overlays.merge(other.overlays)
            self.extra.merge(other.extra)

        empty_namespaces = [key for key, value in self.items() if not value]
        for namespace in empty_namespaces:
            del self[namespace]  # pyright: ignore[reportArgumentType]

        return True

    def copy(self, *, shallow: bool = False) -> Self:
        pack_copy = type(self)().configure(self)

        for key, f in self.extra.items():
            pack_copy.extra[key] = f if shallow else f.copy()

        if self.overlay_parent is None:
            for key, value in self.overlays.items():
                pack_copy.overlays[key] = value.copy(shallow=shallow)

        for key, namespace in self.items():
            namespace_copy = pack_copy[key]
            for key, f in namespace.extra.items():
                namespace_copy.extra[key] = f if shallow else f.copy()
            for key, f in namespace.content:
                namespace_copy[key] = f if shallow else f.copy()

        return pack_copy

    def assign_format(self):
        if (
            self.pack_format is None
            and self.min_format is None
            and self.max_format is None
        ):
            if isinstance(self.latest_pack_format, int):
                if self.latest_pack_format < self.pack_format_switch_format:
                    self.pack_format = self.latest_pack_format
                    self.min_format = None
                    self.max_format = None
                else:
                    self.pack_format = None
                    self.min_format = self.max_format = self.latest_pack_format
            else:
                self.min_format = self.max_format = self.latest_pack_format

    def clear(self):
        self.extra.clear()
        if self.overlay_parent is None:
            self.overlays.clear()
        super().clear()
        self.assign_format()
        if not self.description:
            self.description = ""

    @overload
    def list_files(
        self,
        *extensions: str,
    ) -> Iterator[tuple[str, PackFile]]: ...

    @overload
    def list_files(
        self,
        *extensions: str,
        extend: type[T],
    ) -> Iterator[tuple[str, T]]: ...

    def list_files(
        self,
        *extensions: str,
        extend: Any | None = None,
    ) -> Iterator[tuple[str, Any]]:
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
            yield from namespace.list_files(namespace_name, *extensions, extend=extend)  # pyright: ignore[reportArgumentType]

        if self.overlay_parent is None:
            for overlay in self.overlays.values():
                yield from overlay.list_files(*extensions, extend=extend)  # pyright: ignore[reportArgumentType]

    @overload
    def all(self, *match: str) -> Iterable[tuple[str, NamespaceFile]]: ...

    @overload
    def all(
        self, *match: str, extend: type[NamespaceFileType]
    ) -> Iterable[tuple[str, NamespaceFileType]]: ...

    def all(
        self, *match: str, extend: type[NamespaceFile] | None = None
    ) -> Iterable[tuple[str, NamespaceFile]]:
        """List all the namespaced resources of a specific type, even from overlays."""
        for file_type in self.get_file_types(extend=extend):
            proxy = self[file_type]
            for path in proxy.match(*match or ["*"]):
                yield path, proxy[path]
        if self.overlay_parent is None:
            for overlay in self.overlays.values():
                if extend:
                    yield from overlay.all(*match, extend=extend)
                else:
                    yield from overlay.all(*match)

    @property
    def supported_formats(self) -> SupportedFormats | None:
        if self.overlay_parent is not None:
            overlays: Any = self.overlay_parent.mcmeta.data.get("overlays", {})
            for entry in overlays.get("entries", []):
                if entry.get("directory") == self.overlay_name:
                    return entry.get("formats")
        else:
            return self.mcmeta.data.get("pack", {}).get("supported_formats")

    @supported_formats.setter
    def supported_formats(self, value: SupportedFormats | None):
        if self.overlay_parent is not None:
            overlays: Any = self.overlay_parent.mcmeta.data.setdefault("overlays", {})
            for entry in overlays.setdefault("entries", []):
                if entry.get("directory") == self.overlay_name:
                    if value is None:
                        entry.pop("formats", None)
                    else:
                        entry["formats"] = value
                    break
            else:
                if value is not None:
                    overlays["entries"].append(
                        {"formats": value, "directory": self.overlay_name}
                    )
                else:
                    overlays["entries"].append({"directory": self.overlay_name})
        else:
            if value is None:
                self.mcmeta.data.setdefault("pack", {}).pop("supported_formats", None)
            else:
                self.mcmeta.data.setdefault("pack", {})["supported_formats"] = value

    @property
    def min_format(self) -> FormatSpecifier | None:
        if self.overlay_parent is not None:
            overlays: Any = self.overlay_parent.mcmeta.data.get("overlays", {})
            for entry in overlays.get("entries", []):
                if entry.get("directory") == self.overlay_name:
                    return entry.get("min_format")
        else:
            return self.mcmeta.data.get("pack", {}).get("min_format")

    @min_format.setter
    def min_format(self, value: FormatSpecifier | None):
        if self.overlay_parent is not None:
            overlays: Any = self.overlay_parent.mcmeta.data.setdefault("overlays", {})
            for entry in overlays.setdefault("entries", []):
                if entry.get("directory") == self.overlay_name:
                    if value is None:
                        entry.pop("min_format", None)
                    else:
                        entry["min_format"] = value
                    break
            else:
                if value is not None:
                    overlays["entries"].append(
                        {"directory": self.overlay_name, "min_format": value}
                    )
                else:
                    overlays["entries"].append({"directory": self.overlay_name})
        pack = self.mcmeta.data.setdefault("pack", {})
        if value is None:
            pack.pop("min_format", None)
        else:
            pack["min_format"] = value

    @property
    def max_format(self) -> FormatSpecifier | None:
        if self.overlay_parent is not None:
            overlays: Any = self.overlay_parent.mcmeta.data.get("overlays", {})
            for entry in overlays.get("entries", []):
                if entry.get("directory") == self.overlay_name:
                    return entry.get("max_format")
        else:
            return self.mcmeta.data.get("pack", {}).get("max_format")

    @max_format.setter
    def max_format(self, value: FormatSpecifier | None):
        if self.overlay_parent is not None:
            overlays: Any = self.overlay_parent.mcmeta.data.setdefault("overlays", {})
            for entry in overlays.setdefault("entries", []):
                if entry.get("directory") == self.overlay_name:
                    if value is None:
                        entry.pop("max_format", None)
                    else:
                        entry["max_format"] = value
                    break
            else:
                if value is None:
                    overlays["entries"].append({"directory": self.overlay_name})
                else:
                    overlays["entries"].append(
                        {"directory": self.overlay_name, "max_format": value}
                    )
        pack = self.mcmeta.data.setdefault("pack", {})
        if value is None:
            pack.pop("max_format", None)
        else:
            pack["max_format"] = value

    @classmethod
    def get_extra_info(cls) -> dict[str, type[PackFile]]:
        return {"pack.mcmeta": Mcmeta, "pack.png": PngFile}

    def resolve_extra_info(self) -> dict[str, type[PackFile]]:
        extra_info = self.get_extra_info()
        if self.extend_extra:
            _update_with_none(extra_info, self.extend_extra)
        return extra_info

    def resolve_scope_map(
        self,
    ) -> dict[tuple[tuple[str, ...], str], type[NamespaceFile]]:
        scope_map = dict(self.namespace_type.scope_map)
        for file_type in self.extend_namespace:
            for scope in list_input_scopes(file_type.scope):
                scope_map[scope, file_type.extension] = file_type

        return scope_map

    def resolve_namespace_extra_info(self) -> dict[str, type[PackFile]]:
        namespace_extra_info = self.namespace_type.get_extra_info()
        if self.extend_namespace_extra:
            _update_with_none(namespace_extra_info, self.extend_namespace_extra)
        return namespace_extra_info

    def get_file_types(
        self,
        *extensions: str,
        extend: Any | None = None,
    ) -> Sequence[type[NamespaceFile]]:
        file_types = set(self.resolve_scope_map().values())

        if extensions:
            file_types = {t for t in file_types if t.extension in extensions}
        if extend:
            file_types = {t for t in file_types if issubclass(t, extend)}

        return sorted(file_types, key=lambda t: t.snake_name)

    def load(
        self,
        origin: FileOrigin | None = None,
        extend_extra: Mapping[str, type[PackFile]] | None = None,
        extend_namespace: Iterable[type[NamespaceFile]] = (),
        extend_namespace_extra: Mapping[str, type[PackFile]] | None = None,
        merge_policy: MergePolicy | None = None,
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

        self.assign_format()
        if not self.description:
            self.description = ""

    def mount(
        self,
        prefix: str,
        origin: FileOrigin,
        origin_folders: dict[str, list[PurePath]] | None = None,
    ):
        """Mount files from a zipfile or from the filesystem."""
        files: dict[str, PackFile] = {}

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

        self.merge(namespaces)  # pyright: ignore[reportArgumentType]

        if self.overlay_parent is None:
            overlays: Any = self.mcmeta.data.get("overlays", {})
            for entry in overlays.get("entries", []):
                name = entry.get("directory")
                if name is not None:
                    entry_copy = deepcopy(entry)
                    overlay = self.overlays[name]
                    if (x := entry_copy.get("min_format")) is not None:
                        overlay.min_format = x
                    if (x := entry_copy.get("max_format")) is not None:
                        overlay.max_format = x
                    if (x := entry_copy.get("supported_formats")) is not None:
                        overlay.supported_formats = x
                    overlay.extend_namespace = self.extend_namespace
                    overlay.extend_namespace_extra = self.extend_namespace_extra
                    overlay.mount(prefix, origin, origin_folders)

            remaining_overlays = list(origin_folders)
            for name in remaining_overlays:
                overlay = self.overlays[name]
                overlay.extend_namespace = self.extend_namespace
                overlay.extend_namespace_extra = self.extend_namespace_extra
                overlay.mount(prefix, origin, origin_folders)
                if not overlay:
                    del self.overlays[name]

    def unveil(self, prefix: str, origin: FileSystemPath | UnveilMapping) -> bool:
        """Track mounted resource prefix."""
        if not isinstance(origin, UnveilMapping):
            origin = Path(origin).resolve()

        mounted = self.unveiled.setdefault(origin, set())

        if prefix in mounted:
            return False

        to_remove: set[str] = set()
        for mnt in mounted:
            if prefix.startswith(mnt):
                return False
            if mnt.startswith(prefix):
                to_remove.add(mnt)

        mounted -= to_remove
        mounted.add(prefix)
        return True

    def dump(self, origin: FileOrigin):
        """Write the content of the pack to a zipfile or to the filesystem"""
        _dump_files(origin, self.list_files())

    def save(
        self,
        directory: FileSystemPath | None = None,
        path: FileSystemPath | None = None,
        zipped: bool | None = None,
        compression: Literal["none", "deflate", "bzip2", "lzma"] | None = None,
        compression_level: int | None = None,
        overwrite: bool | None = False,
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
            f"description={self.description!r}, pack_format={self.pack_format!r}, min_format={self.min_format!r}, max_format={self.max_format!r})"
        )


def _dump_files(origin: FileOrigin, files: Iterable[tuple[str, PackFile]]):
    dirs: defaultdict[tuple[str, ...], list[tuple[str, PackFile]]] = defaultdict(list)

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


def _update_with_none(dst: MutableMapping[K, V], src: Mapping[K, V | None]):
    for k, v in list(src.items()):
        if v is None:
            dst.pop(k, None)
        else:
            dst[k] = v


def create_group_map(
    file_types: Mapping[PackType, Iterable[type[NamespaceFile]]],
    plural: bool = False,
) -> dict[str, tuple[list[PackType], type[NamespaceFile]]]:
    group_map: dict[str, tuple[list[PackType], type[NamespaceFile]]] = {}
    for pack, types in file_types.items():
        for t in types:
            group_map.setdefault(t.snake_name, ([], t))[0].append(pack)
    if plural:
        for singular in list(group_map):
            group_map.setdefault(f"{singular}s", group_map[singular])
    return group_map


def list_input_scopes(scope: NamespaceFileScope) -> Iterable[tuple[str, ...]]:
    return [scope] if isinstance(scope, tuple) else scope.values()


def get_output_scope(
    scope: NamespaceFileScope, pack: int | Pack[Any] | None
) -> tuple[str, ...]:
    if isinstance(scope, tuple):
        return scope

    pack_format: None | int | tuple[int] | tuple[int, int] = None
    if pack is None:
        # Fall back to the most recent scope
        pack_format = 9999
    elif isinstance(pack, int):
        pack_format = pack
    else:
        # Use the pack format from the pack's supported_formats.
        # Otherwise, use the pack_format itself
        if pack.max_format:
            if isinstance(pack.max_format, int):
                pack_format = pack.pack_format
            else:
                pack_format = pack.max_format[0]
        elif pack.supported_formats:
            if isinstance(pack.supported_formats, int):
                pack_format = pack.supported_formats
            elif isinstance(pack.supported_formats, list):
                pack_format = pack.supported_formats[1]
            else:
                pack_format = pack.supported_formats["max_inclusive"]
        else:
            pack_format = pack.pack_format
    if pack_format is None:
        # Fall back to the most recent scope
        pack_format = 9999

    result: tuple[str, ...] | None = None
    result_format: int | None = None
    for key, value in scope.items():
        if key <= pack_format and (result_format is None or key > result_format):
            result = value
            result_format = key
    if result is None:
        raise ValueError(f"No scope found for pack format {pack_format} in {scope}")
    return result
