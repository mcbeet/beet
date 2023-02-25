__all__ = [
    "FileOrigin",
    "File",
    "FileSerialize",
    "FileDeserialize",
    "TextFileBase",
    "RawTextFileBase",
    "TextFile",
    "BinaryFileBase",
    "RawBinaryFileBase",
    "BinaryFile",
    "DataModelBase",
    "JsonFileBase",
    "JsonFile",
    "YamlFileBase",
    "YamlFile",
    "PngFileBase",
    "SerializationError",
    "DeserializationError",
    "InvalidDataModel",
]


import io
import json
import shutil
from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass, replace
from pathlib import Path
from types import GenericAlias
from typing import (
    Any,
    Callable,
    ClassVar,
    Generic,
    Mapping,
    Optional,
    TypeGuard,
    TypeVar,
    final,
)
from zipfile import ZipFile

import yaml
from pydantic import BaseModel, ValidationError
from typing_extensions import Self

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
    SENTINEL_OBJ,
    FileSystemPath,
    JsonDict,
    dump_json,
    ensure_subclass_initialized_lazy_field,
    extra_field,
    format_validation_error,
    get_first_generic_param_type,
    is_lazy_field_uninitialized,
    lazy_extra_field,
    model_content,
    snake_case,
)

ValueType = TypeVar("ValueType")
SerializeType = TypeVar("SerializeType")

MutableFileOrigin = FileSystemPath | ZipFile
FileOrigin = MutableFileOrigin | Mapping[str, FileSystemPath]


@dataclass(eq=False, repr=False)
class File(Generic[ValueType, SerializeType], ABC):
    """Base file class."""

    _content: Optional[ValueType | SerializeType] = None
    source_path: Optional[FileSystemPath] = None

    source_start: Optional[int] = extra_field(default=None)
    source_stop: Optional[int] = extra_field(default=None)

    @property
    def source_start_or_default(self) -> int:
        return 0 if self.source_start is None else self.source_start

    @property
    def source_stop_or_default(self) -> int:
        return -1 if self.source_stop is None else self.source_stop

    on_bind: Optional[Callable[[Self, Any, str], Any]] = extra_field(default=None)

    serializer: Callable[[ValueType], SerializeType] = lazy_extra_field()
    deserializer: Callable[[SerializeType], ValueType] = lazy_extra_field()
    reader: Callable[[FileSystemPath, int, int], SerializeType] = lazy_extra_field()

    original: "File[ValueType, SerializeType]" = lazy_extra_field()

    def __post_init__(self):
        ensure_subclass_initialized_lazy_field(self.serializer, "serializer")
        ensure_subclass_initialized_lazy_field(self.deserializer, "deserializer")

        if self._content is self.source_path is None:
            self._content = self.default()

        if is_lazy_field_uninitialized(self.reader):
            self.reader = self.from_path

        if is_lazy_field_uninitialized(self.original):
            self.original = self

    def merge(self, other: Self) -> bool:
        """Merge the given file or return False to indicate no special handling."""
        return False

    def bind(self, pack: Any, path: str) -> Any:
        """Handle file binding."""
        if self.on_bind:
            self.on_bind(self, pack, path)

    def set_content(self, content: ValueType | SerializeType):
        """Update the internal content."""
        if self.source_path:
            self.original = replace(self, original=SENTINEL_OBJ)
            self.source_path = None
            self.source_start = None
            self.source_stop = None
        self._content = content

    def get_content(self) -> ValueType | SerializeType:
        """Return the internal content."""
        return (
            self.reader(
                self.ensure_source_path(),
                self.source_start_or_default,
                self.source_stop_or_default,
            )
            if self._content is None
            else self._content
        )

    def ensure_source_path(self) -> FileSystemPath:
        """Make sure that the file has a source path and return it."""
        if self.source_path:
            return self.source_path

        raise ValueError(
            f"Expected {self.__class__.__name__} object to be initialized with a source path."
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
        if self is other:
            return True

        if type(self) != type(other):
            return NotImplemented

        return (
            (
                self.source_path is not None
                and self.source_path == other.source_path
                and self.source_start_or_default == other.source_start_or_default
                and self.source_stop_or_default == other.source_stop_or_default
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
            f"{cls.__name__} object must be initialized with either a value, serialized data, or a source path."
        )

    def copy(self) -> Self:
        """Copy the file."""
        return replace(self, _content=deepcopy(self._content))

    @abstractmethod
    def is_serialized_type(
        self,
        content: ValueType | SerializeType,
    ) -> TypeGuard[SerializeType]:
        ...

    def is_value_type(self, content: ValueType | SerializeType) -> TypeGuard[ValueType]:
        return not self.is_serialized_type(content)

    def serialize(self, content: ValueType | SerializeType) -> SerializeType:
        """Serialize file content."""
        try:
            # Check for serialized type first in case ValueType is compatible with SerializedType
            if self.is_serialized_type(content):
                return content
            elif self.is_value_type(content):
                return self.serializer(content)
            else:
                raise TypeError("Invalid type for content")
        except BubbleException:
            raise
        except Exception as exc:
            raise SerializationError(self) from exc

    def deserialize(self, content: ValueType | SerializeType) -> ValueType:
        """Deserialize file content."""
        try:
            # Check for value type first in case SerializedType is compatible with ValueType
            if self.is_value_type(content):
                return content
            elif self.is_serialized_type(content):
                return self.deserializer(content)
            else:
                raise TypeError("Invalid type for content")
        except BubbleException:
            raise
        except Exception as exc:
            raise DeserializationError(self) from exc

    @classmethod
    @abstractmethod
    def from_path(cls, path: FileSystemPath, start: int, stop: int) -> SerializeType:
        """Read file content from path."""
        ...

    @classmethod
    @abstractmethod
    def from_zip(cls, origin: ZipFile, name: str) -> SerializeType:
        """Read file content from zip."""
        ...

    @classmethod
    def load(cls, origin: FileOrigin, path: FileSystemPath = "") -> Self:
        """Load a file from a zipfile or from the filesystem."""
        instance = cls.try_load(origin, path)
        if instance is None:
            raise FileNotFoundError(path)
        return instance

    @classmethod
    def try_load(cls, origin: FileOrigin, path: FileSystemPath = "") -> Optional[Self]:
        """Try to load a file from a zipfile or from the filesystem."""
        if isinstance(origin, ZipFile):
            try:
                return cls(cls.from_zip(origin, str(path)))
            except KeyError:
                return None
        elif isinstance(origin, Mapping):
            try:
                path = "" if path == Path() else str(path)
                path = Path(origin[path])
            except KeyError:
                return None
        else:
            path = Path(origin, path)

        return cls(source_path=path) if path.is_file() else None

    @abstractmethod
    def dump_path(self, path: FileSystemPath, raw: SerializeType) -> None:
        """Write file content to path."""
        ...

    @abstractmethod
    def dump_zip(self, origin: ZipFile, name: str, raw: SerializeType) -> None:
        """Write file content to zip."""
        ...

    def dump(self, origin: MutableFileOrigin, path: FileSystemPath):
        """Write the file to a zipfile or to the filesystem."""
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
        content: str

        if self._content is not None:
            content = repr(self._content)
        elif self.source_path:
            content = f"source_path={self.source_path!r}"

            if self.source_start is not None:
                content += f", source_start={self.source_start}"

            if self.source_stop is not None:
                content += f", source_stop={self.source_stop}"
        else:
            content = ""

        return f"{self.__class__.__name__}({content})"


FileType = TypeVar("FileType", bound=File[Any, Any])


class FileSerialize(Generic[SerializeType]):
    """Descriptor that makes sure that content of the file is serialized."""

    def __get__(
        self,
        obj: File[Any, Any],
        objtype: Optional[type[Any]] = None,
    ) -> SerializeType:
        return obj.ensure_serialized()

    def __set__(self, obj: File[Any, Any], value: SerializeType):
        obj.set_content(value)


class FileDeserialize(Generic[ValueType]):
    """Descriptor that makes sure that content of the file is deserialized."""

    def __get__(
        self,
        obj: File[Any, Any],
        objtype: Optional[type[Any]] = None,
    ) -> ValueType:
        return obj.ensure_deserialized()

    def __set__(self, obj: File[Any, Any], value: ValueType):
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

    default_encoding: ClassVar[str] = "utf-8"
    encoding: Optional[str] = extra_field(default=default_encoding)
    errors: Optional[str] = extra_field(default=None)
    newline: Optional[str] = extra_field(default=None)

    text: ClassVar[FileSerialize[str]] = FileSerialize()

    def __post_init__(self):
        if is_lazy_field_uninitialized(self.serializer):
            self.serializer = self.to_str

        if is_lazy_field_uninitialized(self.deserializer):
            self.deserializer = self.from_str

        super().__post_init__()

    def is_serialized_type(self, content: ValueType | str) -> TypeGuard[str]:
        return isinstance(content, str)

    @classmethod
    def from_path(cls, path: FileSystemPath, start: int, stop: int) -> str:
        with open(path, "r", encoding=cls.default_encoding) as f:
            if start > 0:
                f.seek(start)
            return f.read(stop - start) if stop >= -1 else f.read()

    @classmethod
    def from_zip(cls, origin: ZipFile, name: str) -> str:
        return origin.read(name).decode(encoding=cls.default_encoding)

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

    @abstractmethod
    def to_str(self, content: ValueType) -> str:
        """Convert content to string."""
        ...

    @abstractmethod
    def from_str(self, content: str) -> ValueType:
        """Convert string to content."""
        ...


class RawTextFileBase(TextFileBase[str]):
    def is_value_type(self, content: str) -> TypeGuard[str]:
        return True


@final
@dataclass(eq=False, repr=False)
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
        if is_lazy_field_uninitialized(self.serializer):
            self.serializer = self.to_bytes

        if is_lazy_field_uninitialized(self.deserializer):
            self.deserializer = self.from_bytes

        super().__post_init__()

    def is_serialized_type(self, content: ValueType | bytes) -> TypeGuard[bytes]:
        return isinstance(content, bytes)

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

    @abstractmethod
    def to_bytes(self, content: ValueType) -> bytes:
        """Convert content to bytes."""
        ...

    @abstractmethod
    def from_bytes(self, content: bytes) -> ValueType:
        """Convert bytes to content."""
        ...


class RawBinaryFileBase(BinaryFileBase[bytes]):
    def to_bytes(self, content: bytes) -> bytes:
        return content

    def from_bytes(self, content: bytes) -> bytes:
        return content

    def is_value_type(self, content: bytes) -> TypeGuard[bytes]:
        return True


@final
@dataclass(eq=False, repr=False)
class BinaryFile(RawBinaryFileBase):
    """Class representing a binary file."""

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
class DataModelBase(Generic[ValueType], TextFileBase[ValueType]):
    """Base class for data models."""

    encoder: Callable[[Any], str] = lazy_extra_field()
    decoder: Callable[[str], Any] = lazy_extra_field()

    data: FileDeserialize[ValueType] = extra_field(
        default=FileDeserialize[ValueType](), init=False
    )

    base_model: ClassVar[Optional[type[BaseModel]]] = None

    @classmethod
    def model(cls) -> Optional[type[ValueType]]:
        return cls.base_model  # type: ignore

    def __init_subclass__(
        cls, *args: Any, model: Optional[type[ValueType]] = None, **kwargs: Any
    ) -> None:
        if model:
            if issubclass(model, BaseModel):
                cls.base_model = model
            else:
                raise TypeError(
                    "Model type must be None or a subclass of both ValueType and ModelBase"
                )
        elif (
            (value_type := get_first_generic_param_type(cls))
            and isinstance(value_type, type)
            and not isinstance(value_type, GenericAlias)
            and issubclass(value_type, BaseModel)
        ):
            cls.base_model = value_type

        super().__init_subclass__(*args, **kwargs)

    def __post_init__(self):
        ensure_subclass_initialized_lazy_field(self.encoder, "encoder")
        ensure_subclass_initialized_lazy_field(self.decoder, "decoder")

        super().__post_init__()

    def to_str(self, content: ValueType) -> str:
        data: Any = (
            model_content(content)
            if self.base_model and isinstance(content, self.base_model)
            else content
        )

        return self.encoder(data)

    def from_str(self, content: str) -> ValueType:
        value = self.decoder(content)

        if self.base_model:
            try:
                return self.base_model.parse_obj(value)  # type: ignore
            except ValidationError as exc:
                message = format_validation_error(
                    snake_case(self.base_model.__name__), exc
                )
                raise InvalidDataModel(self, message) from exc

        return value

    @classmethod
    def default(cls) -> ValueType:
        return model() if (model := cls.model()) else super().default()


class JsonFileBase(DataModelBase[ValueType]):
    """Base class for json files."""

    def __post_init__(self):
        if is_lazy_field_uninitialized(self.encoder):
            self.encoder = dump_json

        if is_lazy_field_uninitialized(self.decoder):
            self.decoder = json.loads

        super().__post_init__()


@final
@dataclass(eq=False, repr=False)
class JsonFile(JsonFileBase[JsonDict]):
    """Class representing a json file."""

    @classmethod
    def default(cls) -> JsonDict:
        return {}


class YamlFileBase(DataModelBase[ValueType]):
    """Base class for yaml files."""

    def __post_init__(self):
        if is_lazy_field_uninitialized(self.encoder):
            self.encoder = yaml.safe_dump

        if is_lazy_field_uninitialized(self.decoder):
            self.decoder = yaml.safe_load

        super().__post_init__()


@final
@dataclass(eq=False, repr=False)
class YamlFile(YamlFileBase[JsonDict]):
    """Class representing a yaml file."""

    @classmethod
    def default(cls) -> JsonDict:
        return {}


@dataclass(eq=False, repr=False)
class PngFileBase(BinaryFileBase[Image]):
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
