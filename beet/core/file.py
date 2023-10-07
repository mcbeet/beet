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
    "SerializationError",
    "DeserializationError",
    "InvalidDataModel",
]


import io
import json
import shutil
from copy import deepcopy
from dataclasses import dataclass, replace
from pathlib import Path
from typing import (
    Any,
    Callable,
    ClassVar,
    Generic,
    Mapping,
    Optional,
    Type,
    TypeVar,
    Union,
)
from zipfile import ZipFile

import yaml
from pydantic import BaseModel, ValidationError

from .error import BubbleException, WrappedException

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


from .utils import (
    FileSystemPath,
    JsonDict,
    dump_json,
    extra_field,
    format_validation_error,
    snake_case,
)

ValueType = TypeVar("ValueType", bound=Any)
SerializeType = TypeVar("SerializeType", bound=Any)
FileType = TypeVar("FileType", bound="File[Any, Any]")

FileOrigin = Union[FileSystemPath, ZipFile, Mapping[str, FileSystemPath]]
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

    serializer: Callable[[ValueType], SerializeType] = extra_field(default=None)
    deserializer: Callable[[SerializeType], ValueType] = extra_field(default=None)
    reader: Callable[[FileSystemPath, int, int], SerializeType] = extra_field(
        default=None
    )

    original: "File[ValueType, SerializeType]" = extra_field(default=None)

    snake_name: ClassVar[str] = "file"

    def __init_subclass__(cls):
        super().__init_subclass__()
        cls.snake_name = snake_case(cls.__name__)

    def __post_init__(self):
        if self._content is self.source_path is None:
            self._content = self.default()
        if not self.reader:  # type: ignore
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
        if self is other:
            return True

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
            or self.get_content() == other.get_content()
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

    def copy(self: FileType) -> FileType:
        """Copy the file."""
        return replace(self, _content=deepcopy(self._content))

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
    def load(
        cls: Type[FileType],
        origin: FileOrigin,
        path: FileSystemPath = "",
    ) -> FileType:
        """Load a file from a zipfile or from the filesystem."""
        instance = cls.try_load(origin, path)
        if instance is None:
            raise FileNotFoundError(path)
        return instance

    @classmethod
    def try_load(
        cls: Type[FileType],
        origin: FileOrigin,
        path: FileSystemPath = "",
    ) -> Optional[FileType]:
        """Try to load a file from a zipfile or from the filesystem."""
        if isinstance(origin, ZipFile):
            try:
                return cls(cls.from_zip(origin, str(path)))
            except KeyError:
                return None
        elif isinstance(origin, Mapping):
            try:
                path = "" if path == Path() else str(path)
                origin, path = origin[path], ""
            except KeyError:
                return None
        path = Path(origin, path)
        return cls(source_path=path) if path.is_file() else None

    def dump_path(self, path: FileSystemPath, raw: SerializeType) -> None:
        """Write file content to path."""
        raise NotImplementedError()

    def dump_zip(self, origin: ZipFile, name: str, raw: SerializeType) -> None:
        """Write file content to zip."""
        raise NotImplementedError()

    def dump(self, origin: FileOrigin, path: FileSystemPath):
        """Write the file to a zipfile or to the filesystem."""
        if isinstance(origin, Mapping):
            raise TypeError(f'Can\'t dump file "{path}" to read-only mapping.')
        if self._content is None:
            if isinstance(origin, ZipFile):
                origin.write(self.ensure_source_path(), str(path))
            else:
                shutil.copyfile(self.ensure_source_path(), str(Path(origin, path)))
        else:
            raw = self.ensure_serialized()
            if isinstance(origin, ZipFile):
                self.dump_zip(origin, str(path), raw)
            else:
                self.dump_path(Path(origin, path), raw)

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


class SerializationError(WrappedException):
    """Raised when serialization fails."""

    file: File[Any, Any]

    def __init__(self, file: File[Any, Any]):
        super().__init__(file)
        self.file = file

    def __str__(self) -> str:
        if self.file.original.source_path:
            return f'Couldn\'t serialize "{self.file.original.source_path}".'
        return f"Couldn't serialize file of type {type(self.file)}."


class DeserializationError(WrappedException):
    """Raised when deserialization fails."""

    file: File[Any, Any]

    def __init__(self, file: File[Any, Any]):
        super().__init__(file)
        self.file = file

    def __str__(self) -> str:
        if self.file.original.source_path:
            return f'Couldn\'t deserialize "{self.file.original.source_path}".'
        return f"Couldn't deserialize file of type {type(self.file)}."


@dataclass(eq=False, repr=False)
class TextFileBase(File[ValueType, str]):
    """Base class for files that get serialized to strings."""

    encoding: Optional[str] = extra_field(default="utf-8")
    errors: Optional[str] = extra_field(default=None)
    newline: Optional[str] = extra_field(default=None)

    text: ClassVar[FileSerialize[str]] = FileSerialize()

    def __post_init__(self):
        super().__post_init__()
        if not self.serializer:  # type: ignore
            self.serializer = self.to_str
        if not self.deserializer:  # type: ignore
            self.deserializer = self.from_str

    def serialize(self, content: Union[ValueType, str]) -> str:
        try:
            return content if isinstance(content, str) else self.serializer(content)
        except BubbleException:
            raise
        except Exception as exc:
            raise SerializationError(self) from exc

    def deserialize(self, content: Union[ValueType, str]) -> ValueType:
        try:
            return self.deserializer(content) if isinstance(content, str) else content
        except BubbleException:
            raise
        except Exception as exc:
            raise DeserializationError(self) from exc

    @classmethod
    def from_path(cls, path: FileSystemPath, start: int, stop: int) -> str:
        with open(path, "r", encoding="utf-8") as f:
            if start > 0:
                f.seek(start)
            return f.read(stop - start) if stop >= -1 else f.read()

    @classmethod
    def from_zip(cls, origin: ZipFile, name: str) -> str:
        return origin.read(name).decode()

    def dump_path(self, path: FileSystemPath, raw: str) -> None:
        with open(
            path,
            "w",
            encoding=self.encoding,
            errors=self.errors,
            newline=self.newline,
        ) as f:
            f.write(raw)

    def dump_zip(self, origin: ZipFile, name: str, raw: str) -> None:
        with origin.open(name, "w") as f:
            with io.TextIOWrapper(
                f,
                encoding=self.encoding,
                errors=self.errors,
                newline=self.newline,
            ) as text_io:
                text_io.write(raw)

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


@dataclass(eq=False, repr=False)
class BinaryFileBase(File[ValueType, bytes]):
    """Base class for files that get serialized to bytes."""

    blob: ClassVar[FileSerialize[bytes]] = FileSerialize()

    def __post_init__(self):
        super().__post_init__()
        if not self.serializer:  # type: ignore
            self.serializer = self.to_bytes
        if not self.deserializer:  # type: ignore
            self.deserializer = self.from_bytes

    def serialize(self, content: Union[ValueType, bytes]) -> bytes:
        try:
            return content if isinstance(content, bytes) else self.serializer(content)
        except BubbleException:
            raise
        except Exception as exc:
            raise SerializationError(self) from exc

    def deserialize(self, content: Union[ValueType, bytes]) -> ValueType:
        try:
            return self.deserializer(content) if isinstance(content, bytes) else content
        except BubbleException:
            raise
        except Exception as exc:
            raise DeserializationError(self) from exc

    @classmethod
    def from_path(cls, path: FileSystemPath, start: int, stop: int) -> bytes:
        with open(path, "rb") as f:
            if start > 0:
                f.seek(start)
            return f.read() if stop == -1 else f.read(stop - start)

    @classmethod
    def from_zip(cls, origin: ZipFile, name: str) -> bytes:
        return origin.read(name)

    def dump_path(self, path: FileSystemPath, raw: bytes) -> None:
        with open(path, "wb") as f:
            f.write(raw)

    def dump_zip(self, origin: ZipFile, name: str, raw: bytes) -> None:
        with origin.open(name, "w") as f:
            f.write(raw)

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


class InvalidDataModel(DeserializationError):
    """Raised when data model deserialization fails."""

    explanation: str

    def __init__(self, file: File[Any, Any], explanation: str):
        super().__init__(file)
        self.explanation = explanation
        self.hide_wrapped_exception = True

    def __str__(self) -> str:
        if self.file.original.source_path:
            return f'Validation error for "{self.file.original.source_path}".\n\n{self.explanation}'
        return f"Validation error for file of type {type(self.file)}.\n\n{self.explanation}"


@dataclass(eq=False, repr=False)
class DataModelBase(TextFileBase[ValueType]):
    """Base class for data models."""

    encoder: Callable[[Any], str] = extra_field(default=None)
    decoder: Callable[[str], Any] = extra_field(default=None)

    data: ClassVar[FileDeserialize[Any]] = FileDeserialize()

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
            try:
                value = self.model.parse_obj(value)
            except ValidationError as exc:
                message = format_validation_error(snake_case(self.model.__name__), exc)
                raise InvalidDataModel(self, message) from exc
        return value  # type: ignore

    @classmethod
    def default(cls) -> ValueType:
        return cls.model() if cls.model and issubclass(cls.model, BaseModel) else {}  # type: ignore


class JsonFileBase(DataModelBase[ValueType]):
    """Base class for json files."""

    def __post_init__(self):
        super().__post_init__()
        if not self.encoder:  # type: ignore
            self.encoder = dump_json
        if not self.decoder:  # type: ignore
            self.decoder = json.loads


@dataclass(eq=False, repr=False)
class JsonFile(JsonFileBase[JsonDict]):
    """Class representing a json file."""

    data: ClassVar[FileDeserialize[JsonDict]] = FileDeserialize()

    @classmethod
    def default(cls) -> JsonDict:
        return {}


class YamlFileBase(DataModelBase[ValueType]):
    """Base class for yaml files."""

    def __post_init__(self):
        super().__post_init__()
        if not self.encoder:  # type: ignore
            self.encoder = yaml.safe_dump
        if not self.decoder:  # type: ignore
            self.decoder = yaml.safe_load


@dataclass(eq=False, repr=False)
class YamlFile(YamlFileBase[JsonDict]):
    """Class representing a yaml file."""

    data: ClassVar[FileDeserialize[JsonDict]] = FileDeserialize()

    @classmethod
    def default(cls) -> JsonDict:
        return {}


@dataclass(eq=False, repr=False)
class PngFile(BinaryFileBase[Image]):
    """Class representing a png file."""

    image: ClassVar[FileDeserialize[Image]] = FileDeserialize()

    def to_bytes(self, content: Image) -> bytes:
        dst = io.BytesIO()
        content.save(dst, format="png")
        return dst.getvalue()

    def from_bytes(self, content: bytes) -> Image:
        return open_image(io.BytesIO(content))

    @classmethod
    def default(cls) -> Image:
        return new_image("RGBA", (16, 16), "magenta")
