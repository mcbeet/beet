"""Service for fetching and unpacking vanilla resources."""


__all__ = [
    "Vanilla",
    "VanillaOptions",
    "ReleaseRegistry",
    "Release",
    "ClientJar",
    "MANIFEST_URL",
]


from pathlib import Path
from typing import Optional, Union
from zipfile import ZipFile

from pydantic import BaseModel

from beet import (
    LATEST_MINECRAFT_VERSION,
    Cache,
    Container,
    Context,
    DataPack,
    JsonFile,
    ResourcePack,
)
from beet.core.utils import FileSystemPath, log_time

MANIFEST_URL: str = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"


class VanillaOptions(BaseModel):
    version: Optional[str] = None
    manifest: Optional[str] = None


class ClientJar:
    """Class holding information about a client jar."""

    cache: Cache
    path: Path
    assets: ResourcePack
    data: DataPack

    def __init__(self, cache: Cache, path: FileSystemPath):
        self.cache = cache
        self.path = Path(path)
        self.assets = ResourcePack()
        self.data = DataPack()

    def mount(self, prefix: Optional[str] = None) -> "ClientJar":
        """Mount the specified prefix if it's not available already."""
        if not prefix:
            self.mount("assets")
            self.mount("data")
            return self

        if prefix.startswith("assets"):
            path = self.cache.get_path(f"{self.path} vanilla resource pack")
            pack = self.assets
        elif prefix.startswith("data"):
            path = self.cache.get_path(f"{self.path} vanilla data pack")
            pack = self.data
        else:
            return self

        if not path.is_dir():
            with log_time("Extract vanilla pack."):
                pack.load(ZipFile(self.path))
                pack.save(path=path)
                return self

        if pack.path == path.parent:
            return self

        pack.unveil(prefix, path)

        return self


class Release:
    """Class holding information about a minecraft release."""

    cache: Cache
    info: JsonFile

    _client_jar: Optional[ClientJar]

    def __init__(self, cache: Cache, info: JsonFile):
        self.cache = cache
        self.info = info
        self._client_jar = None

    @property
    def type(self) -> str:
        return self.info.data["type"]

    @property
    def client_jar(self) -> ClientJar:
        if not self._client_jar:
            path = self.cache.download(self.info.data["downloads"]["client"]["url"])
            self._client_jar = ClientJar(self.cache, path)
        return self._client_jar

    def mount(self, prefix: Optional[str] = None) -> ClientJar:
        return self.client_jar.mount(prefix)

    @property
    def assets(self) -> ResourcePack:
        return self.mount("assets").assets

    @property
    def data(self) -> DataPack:
        return self.mount("data").data


class ReleaseRegistry(Container[str, Release]):
    """Registry for minecraft releases."""

    cache: Cache
    manifest: JsonFile

    def __init__(
        self,
        cache: Cache,
        manifest: Optional[Union[FileSystemPath, JsonFile]] = None,
    ):
        super().__init__()
        self.cache = cache

        manifest = manifest or MANIFEST_URL

        if isinstance(manifest, str) and manifest.startswith(("http://", "https://")):
            manifest = self.cache.download(manifest)
        if not isinstance(manifest, JsonFile):
            manifest = JsonFile(source_path=manifest)

        self.manifest = manifest

    def missing(self, key: str) -> Release:
        for version in self.manifest.data["versions"]:
            if version["id"] == key:
                info = JsonFile(source_path=self.cache.download(version["url"]))
                return Release(self.cache, info)
        raise KeyError(key)


class Vanilla:
    """Service for fetching and unpacking vanilla resources."""

    cache: Cache
    releases: ReleaseRegistry
    minecraft_version: str

    def __init__(
        self,
        ctx: Optional[Context] = None,
        *,
        cache: Optional[Cache] = None,
        manifest: Optional[Union[FileSystemPath, JsonFile]] = None,
        minecraft_version: Optional[str] = None,
    ):
        opts = ctx and ctx.validate("vanilla", VanillaOptions)

        if cache:
            self.cache = cache
        elif ctx:
            self.cache = ctx.cache["vanilla"]
        else:
            raise ValueError("Cache was not provided.")

        self.releases = ReleaseRegistry(self.cache, manifest or opts and opts.manifest)

        if minecraft_version:
            self.minecraft_version = minecraft_version
        elif opts and opts.version:
            self.minecraft_version = opts.version
        elif ctx:
            self.minecraft_version = ctx.minecraft_version
        else:
            self.minecraft_version = LATEST_MINECRAFT_VERSION

    def mount(self, prefix: Optional[str] = None) -> ClientJar:
        return self.releases[self.minecraft_version].mount(prefix)

    @property
    def assets(self) -> ResourcePack:
        return self.releases[self.minecraft_version].assets

    @property
    def data(self) -> DataPack:
        return self.releases[self.minecraft_version].data
