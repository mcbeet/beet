__all__ = ["File", "PlainTextFile", "BinaryFile", "JsonFile", "PngFile"]


import io
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar, Generic, Optional, Tuple, Type, TypeVar, Union
from zipfile import ZipFile

from PIL import Image as img

from .utils import FileSystemPath, dump_json

T = TypeVar("T")
FileType = TypeVar("FileType", bound="File")


@dataclass
class File(Generic[T]):
    raw: Optional[Union[T, bytes]] = None
    source_path: Optional[FileSystemPath] = None

    path: ClassVar[Tuple[str, ...]]
    extension: ClassVar[str]

    def to_content(self, raw: bytes) -> T:
        raise NotImplementedError()

    def to_bytes(self, content: T) -> bytes:
        raise NotImplementedError()

    @property
    def content(self) -> T:
        if self.raw is None:
            assert self.source_path
            self.raw = Path(self.source_path).read_bytes()
            self.source_path = None
        if isinstance(self.raw, bytes):
            self.raw = self.to_content(self.raw)
        return self.raw

    @content.setter
    def content(self, value: T):
        self.raw = value

    def merge(self: FileType, _other: FileType) -> bool:
        return False

    def bind(self, namespace: Any, path: str):
        pass

    @classmethod
    def load(
        cls: Type[FileType], path: FileSystemPath, zipfile: ZipFile = None
    ) -> FileType:
        return cls(zipfile.read(str(path))) if zipfile else cls(source_path=path)

    def dump(self, path: FileSystemPath, zipfile: ZipFile = None):
        if self.raw is None:
            assert self.source_path
            if zipfile:
                zipfile.write(self.source_path, str(path))
            else:
                shutil.copyfile(self.source_path, str(path))
        else:
            raw = self.raw if isinstance(self.raw, bytes) else self.to_bytes(self.raw)
            if zipfile:
                zipfile.writestr(str(path), raw)
            else:
                Path(path).write_bytes(raw)


@dataclass
class PlainTextFile(File[str]):
    raw: Optional[Union[str, bytes]] = None

    extension = ".txt"

    def to_content(self, raw: bytes) -> str:
        return raw.decode()

    def to_bytes(self, content: str) -> bytes:
        return content.encode()


@dataclass
class BinaryFile(File[bytes]):
    raw: Optional[bytes] = None

    def to_content(self, raw: bytes) -> bytes:
        return raw

    def to_bytes(self, content: bytes) -> bytes:
        return content


@dataclass
class JsonFile(File[dict]):
    raw: Optional[Union[dict, bytes]] = None

    extension = ".json"

    def to_content(self, raw: bytes) -> dict:
        return json.loads(raw.decode())

    def to_bytes(self, content: dict) -> bytes:
        return dump_json(content).encode()


@dataclass
class PngFile(File[img.Image]):
    raw: Optional[Union[img.Image, bytes]] = None

    extension = ".png"

    def to_content(self, raw: bytes) -> img.Image:
        return img.open(io.BytesIO(raw))

    def to_bytes(self, content: img.Image) -> bytes:
        dst = io.BytesIO()
        content.save(dst, format="png")
        return dst.getvalue()
