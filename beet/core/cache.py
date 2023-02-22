__all__ = [
    "CacheTransaction",
    "Cache",
    "CachePin",
    "MultiCache",
    "DownloadManager",
]


import logging
import shutil
from concurrent.futures import Executor, ThreadPoolExecutor
from contextlib import closing, contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from textwrap import indent
from typing import Any, BinaryIO, Callable, ClassVar, Optional, Protocol, TypeVar
from urllib.request import urlopen

from pydantic import BaseModel, Extra, Field

from .container import CV, Container, MatchMixin, Pin
from .utils import (
    FileSystemPath,
    JsonDict,
    format_directory,
    get_import_string,
    import_from_string,
    log_time,
    normalize_string,
)

logger = logging.getLogger(__name__)


class CacheTransaction:
    """Shared transaction for flushing automatically."""

    depth: int

    def __init__(self):
        self.depth = 0

    def enter(self):
        self.depth += 1

    def exit(self) -> bool:
        self.depth -= 1
        return not self.depth


class CacheIndex(BaseModel, extra=Extra.forbid, allow_population_by_field_name=True):
    timestamp: datetime
    expire: Optional[datetime] = None
    data: JsonDict = Field(alias="json", default={})
    finalizers: list[str] = []
    keys: dict[str, str] = {}
    mtime: dict[str, float] = {}


class Cache:
    """An expiring filesystem cache that can store serialized json."""

    deleted: bool
    directory: Path
    index_path: Path
    index: CacheIndex
    transaction: CacheTransaction
    download_manager: "DownloadManager"

    index_file: ClassVar[str] = "index.json"

    def __init__(
        self,
        directory: FileSystemPath,
        transaction: Optional[CacheTransaction] = None,
    ):
        self.deleted = False
        self.directory = Path(directory).resolve()
        self.index_path = self.directory / self.index_file
        self.index = (
            CacheIndex.parse_file(self.index_path)
            if self.index_path.is_file()
            else self.get_initial_index()
        )
        self.transaction = transaction or CacheTransaction()
        self.download_manager = DownloadManager()
        self.flush()

    def get_initial_index(self) -> CacheIndex:
        """Return the initial cache index."""
        return CacheIndex(timestamp=datetime.now())

    def add_finalizer(self, obj: str | Callable[["Cache"], Any]):
        """Register the given handler as finalizer."""
        finalizers = self.index.finalizers
        dotted_path = obj if isinstance(obj, str) else get_import_string(obj)
        if dotted_path not in finalizers:
            finalizers.append(dotted_path)

    @property
    def json(self) -> JsonDict:
        return self.index.data

    @json.setter
    def json(self, value: JsonDict):
        self.index.data = value

    def get_path(self, key: str) -> Path:
        """Return a unique file path associated with the given key."""
        keys = self.index.keys

        if not (path := keys.get(key)):
            _, dot, extension = key[-12:].rpartition(".")
            suffix = normalize_string(extension) if dot else ""
            path = hex(len(keys)) + (suffix and f".{suffix}")
            keys[key] = path

        return self.directory / path

    @contextmanager
    def parallel_downloads(self, max_workers: Optional[int] = None):
        """Launch multiple requests at the same time."""
        with DownloadManager.parallel(max_workers) as parallel_download_manager:
            previous_manager = self.download_manager
            self.download_manager = parallel_download_manager
            try:
                yield
            finally:
                self.download_manager = previous_manager

    def download(self, url: str, path: Optional[FileSystemPath] = None) -> Path:
        """Download and cache a given url."""
        return self.download_manager.download(url, path or self.get_path(url))

    def has_changed(self, *filenames: Optional[FileSystemPath]) -> bool:
        """Return whether any of the given files changed since the last check."""
        mtime = self.index.mtime
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

    def invalidate_changes(self, *filenames: Optional[FileSystemPath]):
        """Reset the modification time of the given files."""
        mtime = self.index.mtime
        for filename in filenames:
            if filename:
                mtime.pop(str(Path(filename)), None)

    @property
    def expire(self) -> Optional[datetime]:
        return self.index.expire

    @expire.setter
    def expire(self, value: Optional[datetime]):
        self.index.expire = value

    def timeout(self, delta: Optional[timedelta] = None, **kwargs: Any) -> "Cache":
        """Invalidate the cache after a given timeout."""
        if not delta:
            delta = timedelta()
        delta += timedelta(**kwargs)
        self.expire = self.index.timestamp + delta
        return self

    def restart_timeout(self):
        """Restart the invalidation timeout."""
        now = datetime.now()

        if self.expire:
            self.expire += now - self.index.timestamp

        self.index.timestamp = now

    def __enter__(self) -> "Cache":
        self.transaction.enter()
        return self

    def __exit__(self, *_):
        if self.transaction.exit():
            self.flush()

    def delete(self):
        """Delete the entire cache."""
        if not self.deleted:
            for finalizer in self.index.finalizers:
                import_from_string(finalizer)(self)

            if self.directory.is_dir():
                shutil.rmtree(self.directory)

            self.index = self.get_initial_index()
            self.deleted = True

    def clear(self):
        """Clear the cache by deleting it and creating it again."""
        self.delete()
        self.deleted = False
        self.flush()

    def dumps(self) -> str:
        """Serialize this cache to a JSON formatted str"""
        return self.index.json(by_alias=True, exclude_defaults=True, indent=2)

    def flush(self):
        """Flush the modifications to the filesystem."""
        if self.deleted:
            return

        if self.expire and self.expire <= datetime.now():
            logger.debug('Cache "%s" expired.', self.directory.name)
            self.clear()
        else:
            self.directory.mkdir(parents=True, exist_ok=True)
            self.index_path.write_text(self.dumps())

    @contextmanager
    def override(self, **data: Any):
        """Temporarily update the json data."""
        to_restore: JsonDict = {}
        to_remove: set[str] = set()

        for key, value in data.items():
            if key in self.json:
                to_restore[key] = self.json[key]
            else:
                to_remove.add(key)
            self.json[key] = value

        try:
            yield self
        finally:
            for key in to_remove:
                del self.json[key]
            self.json.update(to_restore)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({str(self.directory)!r})"

    def __str__(self) -> str:
        line_prefix = "  |  "
        formatted_json = indent(self.dumps(), line_prefix)[len(line_prefix) :]
        contents = indent("\n".join(format_directory(self.directory)), "  |    ")

        return (
            f"Cache {self.index_path.parent.name}:\n"
            f"  |  timestamp = {self.index.timestamp.ctime()}\n"
            f"  |  expire = {self.expire and self.expire.ctime()}\n"
            f"  |  \n"
            f"  |  directory = {self.directory}\n"
            f"{contents}\n"
            f"  |  \n"
            f"  |  json = {formatted_json}"
        )


CacheType = TypeVar("CacheType", bound=Cache)


class SupportsCache(Protocol):
    cache: Cache


class CachePin(Pin[str, CV]):
    """Descriptor that makes cache data accessible through attribute lookup."""

    def forward(self, obj: SupportsCache) -> JsonDict:
        return obj.cache.json


class MultiCache(MatchMixin, Container[str, CacheType]):
    """A container of lazily instantiated named caches."""

    path: Path
    default_cache: str
    gitignore: bool
    cache_type: type[CacheType]
    transaction: CacheTransaction

    def __init__(
        self,
        directory: FileSystemPath,
        default_cache: str = "default",
        gitignore: bool = True,
        cache_type: type[CacheType] = Cache,
    ):
        super().__init__()
        self.path = Path(directory).resolve()
        self.default_cache = default_cache
        self.gitignore = gitignore
        self.cache_type = cache_type
        self.transaction = CacheTransaction()

    def missing(self, key: str) -> CacheType:
        return self.cache_type(self.path / key, self.transaction)

    def __delitem__(self, key: str):
        self[key].delete()
        super().__delitem__(key)

    @property
    def directory(self) -> Path:
        return self[self.default_cache].directory

    @property
    def json(self) -> JsonDict:
        return self[self.default_cache].json

    def __enter__(self) -> "MultiCache[CacheType]":
        self.transaction.enter()
        return self

    def __exit__(self, *_):
        if self.transaction.exit():
            self.flush()

    def preload(self):
        """Preload all the named caches."""
        if not self.path.is_dir():
            return
        for directory in self.path.iterdir():
            if (directory / self.cache_type.index_file).is_file():
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


class DownloadManager:
    """Download manager."""

    executor: Optional[Executor]

    def __init__(self, executor: Optional[Executor] = None):
        self.executor = executor

    @classmethod
    @contextmanager
    def parallel(cls, max_workers: Optional[int] = None):
        """Create a download manager that launches multiple requests at the same time."""
        with ThreadPoolExecutor(max_workers) as executor:
            yield cls(executor)

    def download(self, url: str, path: FileSystemPath) -> Path:
        """Download and cache a given url."""
        path = Path(path)

        if not path.is_file():
            fileobj = path.open("wb")
            if self.executor:
                self.executor.submit(self.retrieve, url, fileobj)
            else:
                self.retrieve(url, fileobj)

        return path

    def retrieve(self, url: str, fileobj: BinaryIO):
        """Retrieve file from url."""
        with log_time('Download "%s".', url), closing(fileobj), urlopen(url) as f:
            fileobj.write(f.read())
