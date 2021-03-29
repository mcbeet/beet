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
    "PngFile",
]


import io
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Generic, Optional, Type, TypeVar, Union
from zipfile import ZipFile

from PIL import Image as img

from .utils import FileSystemPath, JsonDict, dump_json

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

    def ensure_serialized(self) -> SerializeType:
        """Make sure that the content of the file is serialized."""
        content = self.serialize(self.get_content())
        self.set_content(content)
        return content

    def ensure_deserialized(self) -> ValueType:
        """Make sure that the content of the file is deserialized."""
        content = self.deserialize(self.get_content())
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

    @classmethod
    def serialize(cls, content: Union[ValueType, SerializeType]) -> SerializeType:
        """Serialize file content."""
        raise NotImplementedError()

    @classmethod
    def deserialize(cls, content: Union[ValueType, SerializeType]) -> ValueType:
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
        return instance  # type: ignore

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
        self, obj: File[Any, SerializeType], objtype: Optional[Type[Any]] = None
    ) -> SerializeType:
        return obj.ensure_serialized()

    def __set__(self, obj: File[Any, SerializeType], value: SerializeType):
        obj.set_content(value)


class FileDeserialize(Generic[ValueType]):
    """Descriptor that makes sure that content of the file is deserialized."""

    def __get__(
        self, obj: File[ValueType, Any], objtype: Optional[Type[Any]] = None
    ) -> ValueType:
        return obj.ensure_deserialized()

    def __set__(self, obj: File[ValueType, Any], value: ValueType):
        obj.set_content(value)


class TextFileBase(File[ValueType, str]):
    """Base class for files that get serialized to strings."""

    text: FileSerialize[str] = FileSerialize()

    @classmethod
    def serialize(cls, content: Union[ValueType, str]) -> str:
        return content if isinstance(content, str) else cls.to_str(content)

    @classmethod
    def deserialize(cls, content: Union[ValueType, str]) -> ValueType:
        return cls.from_str(content) if isinstance(content, str) else content

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


class BinaryFileBase(File[ValueType, bytes]):
    """Base class for files that get serialized to bytes."""

    blob: FileSerialize[bytes] = FileSerialize()

    @classmethod
    def serialize(cls, content: Union[ValueType, bytes]) -> bytes:
        return content if isinstance(content, bytes) else cls.to_bytes(content)

    @classmethod
    def deserialize(cls, content: Union[ValueType, bytes]) -> ValueType:
        return cls.from_bytes(content) if isinstance(content, bytes) else content

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


class JsonFileBase(TextFileBase[ValueType]):
    """Base class for json files."""

    data: FileDeserialize[ValueType] = FileDeserialize()

    @classmethod
    def default(cls) -> ValueType:
        return {}  # type: ignore

    @classmethod
    def to_str(cls, content: ValueType) -> str:
        return dump_json(content)

    @classmethod
    def from_str(cls, content: str) -> ValueType:
        return json.loads(content)


class JsonFile(JsonFileBase[JsonDict]):
    """Class representing a json file."""

    data: FileDeserialize[JsonDict] = FileDeserialize()


class PngFile(BinaryFileBase[img.Image]):
    """Class representing a png file."""

    image: FileDeserialize[img.Image] = FileDeserialize()

    @classmethod
    def to_bytes(cls, content: img.Image) -> bytes:
        dst = io.BytesIO()
        content.save(dst, format="png")
        return dst.getvalue()

    @classmethod
    def from_bytes(cls, content: bytes) -> img.Image:
        return img.open(io.BytesIO(content))
