__all__ = ["MultiCache", "Cache"]


import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

from .utils import FileSystemPath


class Cache:
    """An expiring filesystem cache that can store serialized json."""

    INDEX_FILE = "index.json"

    def __init__(self, directory: FileSystemPath):
        self.deleted = False
        self.directory = Path(directory).absolute()
        self.index_path = self.directory / self.INDEX_FILE
        self.index = (
            json.loads(self.index_path.read_text())
            if self.index_path.is_file()
            else self.get_initial_index()
        )
        self.flush()

    def get_initial_index(self) -> Dict[str, Any]:
        return {
            "updated_at": datetime.now().isoformat(),
            "expires_at": None,
            "data": {},
        }

    @property
    def data(self) -> Dict[str, Any]:
        return self.index["data"]

    @property
    def expires_at(self) -> Optional[datetime]:
        expires_at = self.index["expires_at"]
        return expires_at and datetime.fromisoformat(expires_at)

    @expires_at.setter
    def expires_at(self, value: Optional[datetime]):
        self.index["expires_at"] = value and value.isoformat()

    def timeout(self, delta: timedelta = None, **kwargs):
        if not delta:
            delta = timedelta()
        delta += timedelta(**kwargs)
        self.expires_at = datetime.fromisoformat(self.index["updated_at"]) + delta

    def __enter__(self) -> "Cache":
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.flush()

    def delete(self):
        if not self.deleted:
            shutil.rmtree(self.directory)
            self.index = self.get_initial_index()
            self.deleted = True

    def clear(self):
        self.delete()
        self.deleted = False
        self.flush()

    def flush(self):
        if self.deleted:
            return

        if self.expires_at and self.expires_at <= datetime.now():
            self.clear()
        else:
            self.directory.mkdir(parents=True, exist_ok=True)
            self.index_path.write_text(json.dumps(self.index, indent=2))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({str(self.directory)!r})"


class MultiCache(Dict[str, Cache]):
    """A container of lazily instantiated named caches."""

    DEFAULT_CACHE = "default"

    def __init__(self, directory: FileSystemPath):
        self.path = Path(directory).absolute()

    def __missing__(self, key: str) -> Cache:
        cache = Cache(self.path / key)
        self[key] = cache
        return cache

    def __delitem__(self, key: str):
        self[key].delete()
        super().__delitem__(key)

    @property
    def directory(self) -> Path:
        return self[self.DEFAULT_CACHE].directory

    @property
    def data(self) -> Dict[str, Any]:
        return self[self.DEFAULT_CACHE].data

    def __enter__(self) -> "MultiCache":
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.flush()

    def delete(self):
        self.clear()
        self.path.rmdir()

    def clear(self):
        cache_names = list(self)
        for name in cache_names:
            del self[name]

    def flush(self):
        for cache in self.values():
            cache.flush()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({str(self.path)!r})"
