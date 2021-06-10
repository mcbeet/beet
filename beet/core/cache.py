__all__ = [
    "MultiCache",
    "Cache",
]


import json
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from textwrap import indent
from typing import Any, ClassVar, Iterator, Optional
from urllib.request import urlopen

from .container import Container, MatchMixin
from .utils import FileSystemPath, JsonDict, dump_json, normalize_string

logger = logging.getLogger(__name__)


class Cache:
    """An expiring filesystem cache that can store serialized json."""

    deleted: bool
    directory: Path
    index_path: Path
    index: JsonDict

    index_file: ClassVar[str] = "index.json"

    def __init__(self, directory: FileSystemPath):
        self.deleted = False
        self.directory = Path(directory).resolve()
        self.index_path = self.directory / self.index_file
        self.index = (
            json.loads(self.index_path.read_text())
            if self.index_path.is_file()
            else self.get_initial_index()
        )
        self.flush()

    def get_initial_index(self) -> JsonDict:
        """Return the initial cache index."""
        return {
            "timestamp": datetime.now().isoformat(),
            "expire": None,
            "json": {},
        }

    @property
    def json(self) -> JsonDict:
        return self.index["json"]

    @json.setter
    def json(self, value: JsonDict):
        self.index["json"] = value

    def get_path(self, key: str) -> Path:
        """Return a unique file path associated with the given key."""
        keys = self.index.setdefault("keys", {})

        if not (path := keys.get(key)):
            _, dot, extension = key[-12:].rpartition(".")
            suffix = normalize_string(extension) if dot else ""
            path = hex(len(keys)) + (suffix and f".{suffix}")
            keys[key] = path

        return self.directory / path

    def download(self, url: str) -> Path:
        """Download and cache a given url."""
        path = self.get_path(url)

        if not path.is_file():
            logger.info(f"Downloading {url}")
            with urlopen(url) as f:
                path.write_bytes(f.read())

        return path

    def has_changed(self, *filenames: Optional[FileSystemPath]) -> bool:
        """Return whether any of the given files changed since the last check."""
        mtime = self.index.setdefault("mtime", {})
        changed = False

        for filename in filenames:
            if not filename:
                continue

            path = Path(filename)
            key = str(path)
            last_modified = path.stat().st_mtime

            if mtime.get(key) != last_modified:
                mtime[key] = last_modified
                changed = True

        return changed

    @property
    def expire(self) -> Optional[datetime]:
        expire = self.index["expire"]
        return expire and datetime.fromisoformat(expire)

    @expire.setter
    def expire(self, value: Optional[datetime]):
        self.index["expire"] = value and value.isoformat()

    def timeout(self, delta: Optional[timedelta] = None, **kwargs: Any) -> "Cache":
        """Invalidate the cache after a given timeout."""
        if not delta:
            delta = timedelta()
        delta += timedelta(**kwargs)
        self.expire = datetime.fromisoformat(self.index["timestamp"]) + delta
        return self

    def restart_timeout(self):
        """Restart the invalidation timeout."""
        now = datetime.now()
        timestamp = datetime.fromisoformat(self.index["timestamp"])

        if self.expire:
            self.expire += now - timestamp

        self.index["timestamp"] = now.isoformat()

    def __enter__(self) -> "Cache":
        return self

    def __exit__(self, *_):
        self.flush()

    def delete(self):
        """Delete the entire cache."""
        if not self.deleted:
            if self.directory.is_dir():
                shutil.rmtree(self.directory)
            self.index = self.get_initial_index()
            self.deleted = True

    def clear(self):
        """Clear the cache by deleting it and creating it again."""
        self.delete()
        self.deleted = False
        self.flush()

    def flush(self):
        """Flush the modifications to the filesystem."""
        if self.deleted:
            return

        if self.expire and self.expire <= datetime.now():
            logger.info(f"Cache {self.directory.name} expired")
            self.clear()
        else:
            self.directory.mkdir(parents=True, exist_ok=True)
            self.index_path.write_text(dump_json(self.index))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({str(self.directory)!r})"

    def __str__(self) -> str:
        formatted_json = indent(dump_json(self.json), "  │  ")[5:]
        contents = indent("\n".join(self._format_directory()), "  │    ")

        return (
            f"Cache {self.index_path.parent.name}:\n"
            f"  │  timestamp = {datetime.fromisoformat(self.index['timestamp']).ctime()}\n"
            f"  │  expire = {self.expire and self.expire.ctime()}\n  │  \n"
            f"  │  directory = {self.directory}\n{contents}\n  │  \n"
            f"  │  json = {formatted_json}"
        )

    def _format_directory(
        self,
        directory: Optional[FileSystemPath] = None,
        prefix: str = "",
    ) -> Iterator[str]:
        entries = list(sorted(Path(directory or self.directory).iterdir()))
        indents = ["├─"] * (len(entries) - 1) + ["└─"]

        for indent, entry in zip(indents, entries):
            yield f"{prefix}{indent} {entry.name}"

            if entry.is_dir():
                indent = "│  " if indent == "├─" else "   "
                yield from self._format_directory(entry, prefix + indent)


class MultiCache(MatchMixin, Container[str, Cache]):
    """A container of lazily instantiated named caches."""

    path: Path
    default_cache: str
    gitignore: bool

    def __init__(
        self,
        directory: FileSystemPath,
        default_cache: str = "default",
        gitignore: bool = True,
    ):
        super().__init__()
        self.path = Path(directory).resolve()
        self.default_cache = default_cache
        self.gitignore = gitignore

    def missing(self, key: str) -> Cache:
        cache = Cache(self.path / key)
        self[key] = cache
        return cache

    def __delitem__(self, key: str):
        self[key].delete()
        super().__delitem__(key)

    @property
    def directory(self) -> Path:
        return self[self.default_cache].directory

    @property
    def json(self) -> JsonDict:
        return self[self.default_cache].json

    def __enter__(self) -> "MultiCache":
        return self

    def __exit__(self, *_):
        self.flush()

    def preload(self):
        """Preload all the named caches."""
        if not self.path.is_dir():
            return
        for directory in self.path.iterdir():
            if (directory / Cache.index_file).is_file():
                assert self[directory.name]

    def clear(self):
        """Clear the entire cache."""
        if self.path.is_dir():
            shutil.rmtree(self.path)
        super().clear()

    def flush(self):
        """Flush the modifications to the filesystem."""
        for cache in self.values():
            cache.flush()
        if (
            self.gitignore
            and self.path.is_dir()
            and not (ignore := self.path / ".gitignore").is_file()
        ):
            ignore.write_text("# Automatically created by beet\n*\n")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({str(self.path)!r})"
