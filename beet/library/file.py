__all__ = [
    "PlainTextFile",
    "BinaryFile",
    "JsonFile",
    "PngFile",
]


import io
import json
from typing import TypeVar

from PIL import Image as img

from beet.core.utils import dump_json

from .base import File


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


T = TypeVar("T")


class JsonFile(File[T]):
    extension = ".json"

    def to_content(self, raw: bytes) -> T:
        return json.loads(raw.decode())

    def to_bytes(self, content: T) -> bytes:
        return dump_json(content).encode()


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
