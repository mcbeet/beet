__all__ = [
    "File",
    "PlainTextFile",
    "BinaryFile",
    "GenericJsonFile",
    "JsonFile",
    "PngFile",
]


import io
import json
import shutil
from dataclasses import InitVar, dataclass
from pathlib import Path
from typing import Any, ClassVar, Generic, Optional, Tuple, Type, TypeVar, Union
from zipfile import ZipFile

from PIL import Image as img

from beet.core.utils import FileSystemPath, JsonDict, dump_json

PackOrigin = Union[FileSystemPath, ZipFile]

T = TypeVar("T")
FileType = TypeVar("FileType", bound="File[object]")


@dataclass
class File(Generic[T]):
    """Base file class.

    All resource pack and data pack files inherit from this class. The
    content of the file is generic and lazy, meaning that derived
    classes are responsible for implementing their own loading strategy,
    but that the code will not be executed until you try to access the
    content of the file.
    """

    value: InitVar[Optional[T]] = None
    raw: Any = None
    source_path: Optional[FileSystemPath] = None

    scope: ClassVar[Tuple[str, ...]] = ()
    extension: ClassVar[str] = ""

    def __post_init__(self, value: Optional[T]):
        if value is not None:
            self.raw = value

    def to_content(self, raw: bytes) -> T:
        """Load file content from bytes."""
        raise NotImplementedError()

    def to_bytes(self, content: T) -> bytes:
        """Serialize file content to bytes."""
        raise NotImplementedError()

    @property
    def data(self) -> bytes:
        if self.raw is None:
            self.data = Path(self._ensure_source_path()).read_bytes()
        elif not isinstance(self.raw, bytes):
            self.raw = self.to_bytes(self.raw)
        return self.raw

    @data.setter
    def data(self, value: bytes):
        self.raw = value
        self.source_path = None

    @property
    def content(self) -> T:
        if self.raw is None:
            self.data = Path(self._ensure_source_path()).read_bytes()
        if isinstance(self.raw, bytes):
            self.raw = self.to_content(self.raw)
        return self.raw

    @content.setter
    def content(self, value: T):
        self.raw = value
        self.source_path = None

    @property
    def text(self) -> str:
        return self.data.decode()

    @text.setter
    def text(self, value: str):
        self.data = value.encode()

    def merge(self: FileType, other: FileType) -> bool:
        """Merge the given file or return False to indicate no special handling."""
        return False

    def bind(self, pack: Any, namespace: str, path: str):
        """Handle insertion."""

    @classmethod
    def load(
        cls: Type[FileType],
        origin: PackOrigin,
        path: FileSystemPath,
    ) -> FileType:
        """Load a file from a zipfile or from the filesystem."""
        return (
            cls(raw=origin.read(str(path)))
            if isinstance(origin, ZipFile)
            else cls(source_path=Path(origin, path))
        )

    @classmethod
    def try_load(
        cls: Type[FileType],
        origin: PackOrigin,
        path: FileSystemPath,
    ) -> Optional[FileType]:
        """Try to load a file from a zipfile or from the filesystem."""
        if isinstance(origin, ZipFile):
            try:
                return cls(raw=origin.read(str(path)))
            except KeyError:
                return None
        path = Path(origin, path)
        return cls(source_path=path) if path.is_file() else None

    def dump(
        self,
        origin: PackOrigin,
        path: FileSystemPath,
    ):
        """Write the file to a zipfile or to the filesystem."""
        if self.raw is None:
            if isinstance(origin, ZipFile):
                origin.write(self._ensure_source_path(), str(path))
            else:
                shutil.copyfile(self._ensure_source_path(), str(Path(origin, path)))
        else:
            raw = self.raw if isinstance(self.raw, bytes) else self.to_bytes(self.raw)
            if isinstance(origin, ZipFile):
                origin.writestr(str(path), raw)
            else:
                Path(origin, path).write_bytes(raw)

    def _ensure_source_path(self) -> FileSystemPath:
        if self.source_path:
            return self.source_path
        raise ValueError(
            f"{self.__class__.__name__} object must be initialized with "
            "either a value, raw bytes or a source path."
        )


class PlainTextFile(File[str]):
    extension = ".txt"

    def to_content(self, raw: bytes) -> str:
        return raw.decode()

    def to_bytes(self, content: str) -> bytes:
        return content.encode()


class BinaryFile(File[bytes]):
    def to_content(self, raw: bytes) -> bytes:
        return raw

    def to_bytes(self, content: bytes) -> bytes:
        return content


class GenericJsonFile(File[T]):
    extension = ".json"

    def to_content(self, raw: bytes) -> T:
        return json.loads(raw.decode())

    def to_bytes(self, content: T) -> bytes:
        return dump_json(content).encode()


class JsonFile(GenericJsonFile[JsonDict]):
    pass


class PngFile(File[img.Image]):
    extension = ".png"

    def to_content(self, raw: bytes) -> img.Image:
        return img.open(io.BytesIO(raw))

    def to_bytes(self, content: img.Image) -> bytes:
        dst = io.BytesIO()
        content.save(dst, format="png")
        return dst.getvalue()

    def __eq__(self, other: object) -> bool:
        if result := super().__eq__(other):
            return result
        if isinstance(other, PngFile):
            return type(self) == type(other) and (
                self.to_bytes(self.content) == other.to_bytes(other.content)
            )
        return False
