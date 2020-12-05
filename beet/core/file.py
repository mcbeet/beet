__all__ = [
    "File",
    "FileOrigin",
    "FileValueAlias",
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
from typing import Any, Generic, Optional, Type, TypeVar, Union, cast
from zipfile import ZipFile

from PIL import Image as img

from .utils import FileSystemPath, JsonDict, dump_json

ValueType = TypeVar("ValueType")
SerializeType = TypeVar("SerializeType")
FileType = TypeVar("FileType", bound="File[object, object]")

FileOrigin = Union[FileSystemPath, ZipFile]
TextFileContent = Union[ValueType, str, None]
BinaryFileContent = Union[ValueType, bytes, None]


# TODO: Docstrings


@dataclass
class File(Generic[ValueType, SerializeType]):
    """Base file class.

    All resource pack and data pack files inherit from this class. The
    content of the file is generic and lazy, meaning that derived
    classes are responsible for implementing their own loading strategy,
    but that the code will not be executed until you try to access the
    content of the file.
    """

    content: Union[ValueType, SerializeType, None] = None
    source_path: Optional[FileSystemPath] = None

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

    @property
    def value(self) -> ValueType:
        content = self.deserialize(self.get_content())
        self.set_content(content)
        return content

    @value.setter
    def value(self, value: ValueType):
        self.set_content(value)

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
        return cast(FileType, instance)

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
            raw = self.encode(self.serialize(self.get_content()))
            if isinstance(origin, ZipFile):
                origin.writestr(str(path), raw)
            else:
                Path(origin, path).write_bytes(raw)

    def ensure_source_path(self) -> FileSystemPath:
        """Make sure that the file has a source path and return it."""
        if self.source_path:
            return self.source_path
        raise ValueError(
            f"{self.__class__.__name__} object must be initialized with "
            "either a value, raw bytes or a source path."
        )


class FileValueAlias(Generic[ValueType]):
    def __get__(
        self, obj: File[ValueType, object], objtype: Optional[Type[object]] = None
    ) -> ValueType:
        return obj.value

    def __set__(self, obj: File[ValueType, object], value: ValueType):
        obj.value = value


class TextFileBase(File[ValueType, str]):
    @classmethod
    def serialize(cls, content: Any) -> str:
        return content if isinstance(content, str) else cls.to_str(content)

    @classmethod
    def deserialize(cls, content: Any) -> ValueType:
        return (
            cls.from_str(content)
            if isinstance(content, str)
            else cast(ValueType, content)
        )

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

    @property
    def text(self) -> str:
        content = self.serialize(self.get_content())
        self.set_content(content)
        return content

    @text.setter
    def text(self, text: str):
        self.set_content(text)


class TextFile(TextFileBase[str]):
    @classmethod
    def to_str(cls, content: str) -> str:
        return content

    @classmethod
    def from_str(cls, content: str) -> str:
        return content


class BinaryFileBase(File[ValueType, bytes]):
    @classmethod
    def serialize(cls, content: Any) -> bytes:
        return content if isinstance(content, bytes) else cls.to_bytes(content)

    @classmethod
    def deserialize(cls, content: Any) -> ValueType:
        return (
            cls.from_bytes(content)
            if isinstance(content, bytes)
            else cast(ValueType, content)
        )

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

    @property
    def blob(self) -> bytes:
        content = self.serialize(self.get_content())
        self.set_content(content)
        return content

    @blob.setter
    def blob(self, value: bytes):
        self.set_content(value)


class BinaryFile(BinaryFileBase[bytes]):
    @classmethod
    def to_bytes(cls, content: bytes) -> bytes:
        return content

    @classmethod
    def from_bytes(cls, content: bytes) -> bytes:
        return content


class JsonFileBase(TextFileBase[ValueType]):
    data = FileValueAlias[ValueType]()

    @classmethod
    def to_str(cls, content: ValueType) -> str:
        return dump_json(content)

    @classmethod
    def from_str(cls, content: str) -> ValueType:
        return json.loads(content)


class JsonFile(JsonFileBase[JsonDict]):
    data = FileValueAlias[JsonDict]()


class PngFile(BinaryFileBase[img.Image]):
    image = FileValueAlias[img.Image]()

    @classmethod
    def to_bytes(cls, content: img.Image) -> bytes:
        dst = io.BytesIO()
        content.save(dst, format="png")
        return dst.getvalue()

    @classmethod
    def from_bytes(cls, content: bytes) -> img.Image:
        return img.open(io.BytesIO(content))

    def __eq__(self, other: object) -> bool:
        if result := super().__eq__(other):
            return result
        if isinstance(other, PngFile):
            return type(self) == type(other) and (
                self.serialize(self.get_content())
                == other.serialize(other.get_content())
            )
        return False
