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
    "JsonFileBase",
    "JsonFile",
    "YamlFileBase",
    "YamlFile",
    "PngFile",
]


import io
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Generic, Optional, Type, TypeVar, Union
from zipfile import ZipFile

import yaml

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

ValueType = TypeVar("ValueType")
SerializeType = TypeVar("SerializeType")
FileType = TypeVar("FileType", bound="File[Any, Any]")

FileOrigin = Union[FileSystemPath, ZipFile]
TextFileContent = Union[ValueType, str, None]
BinaryFileContent = Union[ValueType, bytes, None]


@dataclass
class File(Generic[ValueType, SerializeType]):
    """Base file class."""

    content: Union[ValueType, SerializeType, None] = None
    source_path: Optional[FileSystemPath] = None

    serializer: Callable[[ValueType], SerializeType] = extra_field(init=False)
    deserializer: Callable[[SerializeType], ValueType] = extra_field(init=False)

    def __post_init__(self):
        if self.content is self.source_path is None:
            self.content = self.default()

    def merge(self: FileType, other: FileType) -> bool:
        """Merge the given file or return False to indicate no special handling."""
        return False

    def set_content(self, content: Union[ValueType, SerializeType]):
        """Update the internal content."""
        self.content = content
        self.source_path = None

    def get_content(self) -> Union[ValueType, SerializeType]:
        """Return the internal content."""
        return (
            self.decode(Path(self.ensure_source_path()).read_bytes())
            if self.content is None
            else self.content
        )

    def ensure_source_path(self) -> FileSystemPath:
        """Make sure that the file has a source path and return it."""
        if self.source_path:
            return self.source_path
        raise ValueError(
            f"Expected {self.__class__.__name__} object to be initialized with "
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
        return content

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
        return content

    def __eq__(self, other: Any) -> bool:
        if type(self) != type(other):
            return NotImplemented

        return (
            (self.source_path is not None and self.source_path == other.source_path)
            or self.ensure_serialized() == other.ensure_serialized()
            or self.ensure_deserialized() == other.ensure_deserialized()
        )

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
    def decode(cls, raw: bytes) -> SerializeType:
        """Convert bytes to serialized representation."""
        raise NotImplementedError()

    @classmethod
    def encode(cls, raw: SerializeType) -> bytes:
        """Convert serialized representation to bytes."""
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
                return cls(cls.decode(origin.read(str(path))))
            except KeyError:
                return None
        path = Path(origin, path)
        return cls(source_path=path) if path.is_file() else None

    def dump(self, origin: FileOrigin, path: FileSystemPath):
        """Write the file to a zipfile or to the filesystem."""
        if self.content is None:
            if isinstance(origin, ZipFile):
                origin.write(self.ensure_source_path(), str(path))
            else:
                shutil.copyfile(self.ensure_source_path(), str(Path(origin, path)))
        else:
            raw = self.encode(self.ensure_serialized())
            if isinstance(origin, ZipFile):
                origin.writestr(str(path), raw)
            else:
                Path(origin, path).write_bytes(raw)


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
    def decode(cls, raw: bytes) -> str:
        return raw.decode()

    @classmethod
    def encode(cls, raw: str) -> bytes:
        return raw.encode()

    @classmethod
    def to_str(cls, content: ValueType) -> str:
        """Convert content to string."""
        raise NotImplementedError()

    @classmethod
    def from_str(cls, content: str) -> ValueType:
        """Convert string to content."""
        raise NotImplementedError()


class TextFile(TextFileBase[str]):
    """Class representing a text file."""

    @classmethod
    def to_str(cls, content: str) -> str:
        return content

    @classmethod
    def from_str(cls, content: str) -> str:
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
    def decode(cls, raw: bytes) -> bytes:
        return raw

    @classmethod
    def encode(cls, raw: bytes) -> bytes:
        return raw

    @classmethod
    def to_bytes(cls, content: ValueType) -> bytes:
        """Convert content to bytes."""
        raise NotImplementedError()

    @classmethod
    def from_bytes(cls, content: bytes) -> ValueType:
        """Convert bytes to content."""
        raise NotImplementedError()


class BinaryFile(BinaryFileBase[bytes]):
    """Class representing a binary file."""

    @classmethod
    def to_bytes(cls, content: bytes) -> bytes:
        return content

    @classmethod
    def from_bytes(cls, content: bytes) -> bytes:
        return content

    @classmethod
    def default(cls) -> bytes:
        return b""


class JsonFileBase(TextFileBase[ValueType]):
    """Base class for json files."""

    data: FileDeserialize[ValueType] = FileDeserialize()

    @classmethod
    def to_str(cls, content: ValueType) -> str:
        return dump_json(content)

    @classmethod
    def from_str(cls, content: str) -> ValueType:
        return json.loads(content)


class JsonFile(JsonFileBase[JsonDict]):
    """Class representing a json file."""

    data: FileDeserialize[JsonDict] = FileDeserialize()

    @classmethod
    def default(cls) -> JsonDict:
        return {}


class YamlFileBase(TextFileBase[ValueType]):
    """Base class for yaml files."""

    data: FileDeserialize[ValueType] = FileDeserialize()

    @classmethod
    def to_str(cls, content: ValueType) -> str:
        return yaml.dump(content)  # type: ignore

    @classmethod
    def from_str(cls, content: str) -> ValueType:
        return yaml.safe_load(content)


class YamlFile(YamlFileBase[JsonDict]):
    """Class representing a yaml file."""

    data: FileDeserialize[JsonDict] = FileDeserialize()

    @classmethod
    def default(cls) -> JsonDict:
        return {}


class PngFile(BinaryFileBase[Image]):
    """Class representing a png file."""

    image: FileDeserialize[Image] = FileDeserialize()

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
