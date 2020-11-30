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
from typing import Any, ClassVar, Generic, Optional, Tuple, Type, TypeVar
from zipfile import ZipFile

from PIL import Image as img

from beet.core.utils import FileSystemPath, JsonDict, dump_json

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
    def content(self) -> T:
        if self.raw is None:
            self.raw = Path(self._ensure_source_path()).read_bytes()
            self.source_path = None
        if isinstance(self.raw, bytes):
            self.raw = self.to_content(self.raw)
        return self.raw

    @content.setter
    def content(self, value: T):
        self.raw = value

    def merge(self: FileType, other: FileType) -> bool:
        """Merge the given file or return False to indicate no special handling."""
        return False

    def bind(self, pack: Any, namespace: str, path: str):
        """Handle insertion."""

    @classmethod
    def load(
        cls: Type[FileType],
        path: FileSystemPath,
        zipfile: Optional[ZipFile] = None,
    ) -> FileType:
        """Load file from a zipfile or from the filesystem."""
        return cls(raw=zipfile.read(str(path))) if zipfile else cls(source_path=path)

    @classmethod
    def load_if_exists(
        cls: Type[FileType],
        path: FileSystemPath,
        zipfile: Optional[ZipFile] = None,
    ) -> Optional[FileType]:
        """Try to load the file if it exists."""
        if not zipfile and not Path(path).exists():
            return None
        try:
            return cls.load(path, zipfile)
        except KeyError:
            return None

    def dump(
        self,
        path: FileSystemPath,
        zipfile: Optional[ZipFile] = None,
    ):
        """Write the file to a zipfile or to the filesystem."""
        if self.raw is None:
            if zipfile:
                zipfile.write(self._ensure_source_path(), str(path))
            else:
                shutil.copyfile(self._ensure_source_path(), str(path))
        else:
            raw = self.raw if isinstance(self.raw, bytes) else self.to_bytes(self.raw)
            if zipfile:
                zipfile.writestr(str(path), raw)
            else:
                Path(path).write_bytes(raw)

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
