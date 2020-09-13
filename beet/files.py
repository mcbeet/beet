__all__ = ["PlainTextFile", "BinaryFile", "JsonFile", "PngFile"]


import io
import json
from dataclasses import dataclass
from typing import Optional, Union

from PIL import Image as img

from .core import File
from .utils import dump_json


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
