__all__ = [
    "File",
    "FileOrigin",
    "FileSerialize",
    "FileDeserialize",
    "TextFileBase",
    "TextFileContent",
    "TextFile",
    "BinaryFileBase",
    "BinaryFileContent",
    "BinaryFile",
    "DataModelBase",
    "JsonFileBase",
    "JsonFile",
    "YamlFileBase",
    "YamlFile",
    "PngFile",
]


import io
import json
import shutil
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Callable, ClassVar, Generic, Optional, Type, TypeVar, Union
from zipfile import ZipFile

import yaml
from pydantic import BaseModel

try:
    from PIL.Image import Image
    from PIL.Image import new as new_image
    from PIL.Image import open as open_image
except ImportError:
    Image = Any

    def new_image(*args: Any, **kwargs: Any) -> Any:
        raise RuntimeError("Please install Pillow to create images programmatically")

    def open_image(*args: Any, **kwargs: Any) -> Any:
        raise RuntimeError("Please install Pillow to edit images programmatically")


from .utils import FileSystemPath, JsonDict, dump_json, extra_field

ValueType = TypeVar("ValueType", bound=Any)
SerializeType = TypeVar("SerializeType", bound=Any)
FileType = TypeVar("FileType", bound="File[Any, Any]")

FileOrigin = Union[FileSystemPath, ZipFile]
TextFileContent = Union[ValueType, str, None]
BinaryFileContent = Union[ValueType, bytes, None]


@dataclass(eq=False, repr=False)
class File(Generic[ValueType, SerializeType]):
    """Base file class."""

    _content: Union[ValueType, SerializeType, None] = None
    source_path: Optional[FileSystemPath] = None

    source_start: Optional[int] = extra_field(default=None)
    source_stop: Optional[int] = extra_field(default=None)

    on_bind: Optional[Callable[[Any, Any, str], Any]] = extra_field(default=None)

    serializer: Callable[[ValueType], SerializeType] = extra_field(init=False)
    deserializer: Callable[[SerializeType], ValueType] = extra_field(init=False)
    reader: Callable[[FileSystemPath, int, int], SerializeType] = extra_field(
        init=False
    )

    original: "File[ValueType, SerializeType]" = extra_field(default=None)

    def __post_init__(self):
        if self._content is self.source_path is None:
            self._content = self.default()
        self.reader = self.from_path
        if not self.original:
            self.original = self

    def merge(self: FileType, other: FileType) -> bool:
        """Merge the given file or return False to indicate no special handling."""
        return False

    def bind(self, pack: Any, path: str) -> Any:
        """Handle file binding."""
        if self.on_bind:
            self.on_bind(self, pack, path)

    def set_content(self, content: Union[ValueType, SerializeType]):
        """Update the internal content."""
        if self.source_path:
            self.original = replace(self, original=None)
            self.source_path = None
            self.source_start = None
            self.source_stop = None
        self._content = content

    def get_content(self) -> Union[ValueType, SerializeType]:
        """Return the internal content."""
        return (
            self.reader(
                self.ensure_source_path(),
                0 if self.source_start is None else self.source_start,
                -1 if self.source_stop is None else self.source_stop,
            )
            if self._content is None
            else self._content
        )

    def ensure_source_path(self) -> FileSystemPath:
        """Make sure that the file has a source path and return it."""
        if self.source_path:
            return self.source_path
        raise ValueError(
            f"Expected {self.__class__.__name__} object to be initialized with "  # type: ignore
            "a source path."
        )

    def ensure_serialized(
        self,
        serializer: Optional[Callable[[ValueType], SerializeType]] = None,
    ) -> SerializeType:
        """Make sure that the content of the file is serialized."""
        backup = self.serializer
        if serializer:
            self.serializer = serializer

        try:
            content = self.serialize(self.get_content())
        finally:
            self.serializer = backup

        self.set_content(content)
        return content  # type: ignore

    def ensure_deserialized(
        self,
        deserializer: Optional[Callable[[SerializeType], ValueType]] = None,
    ) -> ValueType:
        """Make sure that the content of the file is deserialized."""
        backup = self.deserializer
        if deserializer:
            self.deserializer = deserializer

        try:
            content = self.deserialize(self.get_content())
        finally:
            self.deserializer = backup

        self.set_content(content)
        return content  # type: ignore

    def __eq__(self, other: Any) -> bool:
        if type(self) != type(other):
            return NotImplemented

        return (
            (
                self.source_path is not None
                and self.source_path == other.source_path
                and (0 if self.source_start is None else self.source_start)
                == (0 if other.source_start is None else other.source_start)
                and (-1 if self.source_stop is None else self.source_stop)
                == (-1 if other.source_stop is None else other.source_stop)
            )
            or self.ensure_serialized() == other.ensure_serialized()
            or self.ensure_deserialized() == other.ensure_deserialized()
        )

    def __hash__(self) -> int:
        return id(self)

    @classmethod
    def default(cls) -> ValueType:
        """Return the file's default value."""
        raise ValueError(
            f"{cls.__name__} object must be initialized with "
            "either a value, serialized data, or a source path."
        )

    def serialize(self, content: Union[ValueType, SerializeType]) -> SerializeType:
        """Serialize file content."""
        raise NotImplementedError()

    def deserialize(self, content: Union[ValueType, SerializeType]) -> ValueType:
        """Deserialize file content."""
        raise NotImplementedError()

    @classmethod
    def from_path(cls, path: FileSystemPath, start: int, stop: int) -> SerializeType:
        """Read file content from path."""
        raise NotImplementedError()

    @classmethod
    def from_zip(cls, origin: ZipFile, name: str) -> SerializeType:
        """Read file content from zip."""
        raise NotImplementedError()

    @classmethod
    def load(cls: Type[FileType], origin: FileOrigin, path: FileSystemPath) -> FileType:
        """Load a file from a zipfile or from the filesystem."""
        instance = cls.try_load(origin, path)
        if instance is None:
            raise FileNotFoundError(path)
        return instance

    @classmethod
    def try_load(
        cls: Type[FileType], origin: FileOrigin, path: FileSystemPath
    ) -> Optional[FileType]:
        """Try to load a file from a zipfile or from the filesystem."""
        if isinstance(origin, ZipFile):
            try:
                return cls(cls.from_zip(origin, str(path)))
            except KeyError:
                return None
        path = Path(origin, path)
        return cls(source_path=path) if path.is_file() else None

    def dump(self, origin: FileOrigin, path: FileSystemPath):
        """Write the file to a zipfile or to the filesystem."""
        if self._content is None:
            if isinstance(origin, ZipFile):
                origin.write(self.ensure_source_path(), str(path))
            else:
                shutil.copyfile(self.ensure_source_path(), str(Path(origin, path)))
        else:
            raw = self.ensure_serialized()
            if isinstance(origin, ZipFile):
                origin.writestr(str(path), raw)
            elif isinstance(raw, str):
                Path(origin, path).write_text(raw)
            else:
                Path(origin, path).write_bytes(raw)

    def __repr__(self) -> str:
        content = (
            repr(self._content)
            if self._content is not None
            else f"source_path={self.source_path!r}"
            + (self.source_start is not None) * f", source_start={self.source_start}"
            + (self.source_stop is not None) * f", source_stop={self.source_stop}"
            if self.source_path
            else ""
        )
        return f"{self.__class__.__name__}({content})"


class FileSerialize(Generic[SerializeType]):
    """Descriptor that makes sure that content of the file is serialized."""

    def __get__(
        self,
        obj: File[Any, SerializeType],
        objtype: Optional[Type[Any]] = None,
    ) -> SerializeType:
        return obj.ensure_serialized()

    def __set__(self, obj: File[Any, SerializeType], value: SerializeType):
        obj.set_content(value)


class FileDeserialize(Generic[ValueType]):
    """Descriptor that makes sure that content of the file is deserialized."""

    def __get__(
        self,
        obj: File[ValueType, Any],
        objtype: Optional[Type[Any]] = None,
    ) -> ValueType:
        return obj.ensure_deserialized()

    def __set__(self, obj: File[ValueType, Any], value: ValueType):
        obj.set_content(value)


class TextFileBase(File[ValueType, str]):
    """Base class for files that get serialized to strings."""

    text: FileSerialize[str] = FileSerialize()

    def __post_init__(self):
        super().__post_init__()
        self.serializer = self.to_str
        self.deserializer = self.from_str

    def serialize(self, content: Union[ValueType, str]) -> str:
        return content if isinstance(content, str) else self.serializer(content)

    def deserialize(self, content: Union[ValueType, str]) -> ValueType:
        return self.deserializer(content) if isinstance(content, str) else content

    @classmethod
    def from_zip(cls, origin: ZipFile, name: str) -> str:
        return origin.read(name).decode()

    @classmethod
    def from_path(cls, path: FileSystemPath, start: int, stop: int) -> str:
        with open(path, "r") as f:
            if start > 0:
                f.seek(start)
            return f.read(stop - start) if stop >= -1 else f.read()

    def to_str(self, content: ValueType) -> str:
        """Convert content to string."""
        raise NotImplementedError()

    def from_str(self, content: str) -> ValueType:
        """Convert string to content."""
        raise NotImplementedError()


class TextFile(TextFileBase[str]):
    """Class representing a text file."""

    def to_str(self, content: str) -> str:
        return content

    def from_str(self, content: str) -> str:
        return content

    @classmethod
    def default(cls) -> str:
        return ""


class BinaryFileBase(File[ValueType, bytes]):
    """Base class for files that get serialized to bytes."""

    blob: FileSerialize[bytes] = FileSerialize()

    def __post_init__(self):
        super().__post_init__()
        self.serializer = self.to_bytes
        self.deserializer = self.from_bytes

    def serialize(self, content: Union[ValueType, bytes]) -> bytes:
        return content if isinstance(content, bytes) else self.serializer(content)

    def deserialize(self, content: Union[ValueType, bytes]) -> ValueType:
        return self.deserializer(content) if isinstance(content, bytes) else content

    @classmethod
    def from_zip(cls, origin: ZipFile, name: str) -> bytes:
        return origin.read(name)

    @classmethod
    def from_path(cls, path: FileSystemPath, start: int, stop: int) -> bytes:
        with open(path, "rb") as f:
            if start > 0:
                f.seek(start)
            return f.read() if stop == -1 else f.read(stop - start)

    def to_bytes(self, content: ValueType) -> bytes:
        """Convert content to bytes."""
        raise NotImplementedError()

    def from_bytes(self, content: bytes) -> ValueType:
        """Convert bytes to content."""
        raise NotImplementedError()


class BinaryFile(BinaryFileBase[bytes]):
    """Class representing a binary file."""

    def to_bytes(self, content: bytes) -> bytes:
        return content

    def from_bytes(self, content: bytes) -> bytes:
        return content

    @classmethod
    def default(cls) -> bytes:
        return b""


@dataclass(eq=False, repr=False)
class DataModelBase(TextFileBase[ValueType]):
    """Base class for data models."""

    encoder: Callable[[Any], str] = extra_field(init=False)
    decoder: Callable[[str], Any] = extra_field(init=False)

    data = FileDeserialize[ValueType]()

    model: ClassVar[Optional[Type[Any]]] = None

    def to_str(self, content: ValueType) -> str:
        if (
            self.model
            and issubclass(self.model, BaseModel)
            and isinstance(content, self.model)
        ):
            content = content.dict()  # type: ignore
            if self.model.__custom_root_type__:
                content = content["__root__"]
        return self.encoder(content)

    def from_str(self, content: str) -> ValueType:
        value = self.decoder(content)
        if self.model and issubclass(self.model, BaseModel):
            value = self.model.parse_obj(value)
        return value  # type: ignore

    @classmethod
    def default(cls) -> ValueType:
        return cls.model() if cls.model and issubclass(cls.model, BaseModel) else {}  # type: ignore


class JsonFileBase(DataModelBase[ValueType]):
    """Base class for json files."""

    def __post_init__(self):
        super().__post_init__()
        self.encoder = dump_json
        self.decoder = json.loads


class JsonFile(JsonFileBase[JsonDict]):
    """Class representing a json file."""

    data = FileDeserialize[JsonDict]()

    @classmethod
    def default(cls) -> JsonDict:
        return {}


class YamlFileBase(DataModelBase[ValueType]):
    """Base class for yaml files."""

    def __post_init__(self):
        super().__post_init__()
        self.encoder = yaml.safe_dump
        self.decoder = yaml.safe_load


class YamlFile(YamlFileBase[JsonDict]):
    """Class representing a yaml file."""

    data = FileDeserialize[JsonDict]()

    @classmethod
    def default(cls) -> JsonDict:
        return {}


class PngFile(BinaryFileBase[Image]):
    """Class representing a png file."""

    image = FileDeserialize[Image]()

    @classmethod
    def to_bytes(cls, content: Image) -> bytes:
        dst = io.BytesIO()
        content.save(dst, format="png")
        return dst.getvalue()

    @classmethod
    def from_bytes(cls, content: bytes) -> Image:
        return open_image(io.BytesIO(content))

    @classmethod
    def default(cls) -> Image:
        return new_image("RGB", (16, 16), "black")
