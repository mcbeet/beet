"""Service for fetching and unpacking vanilla resources."""


__all__ = [
    "Vanilla",
    "VanillaOptions",
    "ReleaseRegistry",
    "Release",
    "ClientJar",
    "AssetIndex",
    "MANIFEST_URL",
    "RESOURCES_URL",
]


from pathlib import Path
from typing import Iterator, Optional, Union
from zipfile import ZipFile

from beet import (
    LATEST_MINECRAFT_VERSION,
    Cache,
    Container,
    Context,
    DataPack,
    JsonFile,
    PluginOptions,
    ResourcePack,
    UnveilMapping,
)
from beet.contrib.worldgen import worldgen
from beet.core.utils import FileSystemPath, log_time

MANIFEST_URL: str = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
RESOURCES_URL: str = "https://resources.download.minecraft.net"


class VanillaOptions(PluginOptions):
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
        worldgen(self.data)

    def mount(
        self,
        prefix: Optional[str] = None,
        object_mapping: Optional[UnveilMapping] = None,
    ) -> "ClientJar":
        """Mount the specified prefix if it's not available already."""
        if not prefix:
            self.mount("assets", object_mapping)
            self.mount("data", object_mapping)
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
        elif pack.path != path.parent:
            pack.unveil(prefix, path)

        if object_mapping and isinstance(pack, ResourcePack):
            with self.cache.parallel_downloads():
                pack.unveil(prefix, object_mapping)

        return self


class AssetIndex(Container[str, FileSystemPath]):
    """Class for retrieving assets referenced by a particular release."""

    cache: Cache
    info: JsonFile

    def __init__(self, cache: Cache, info: JsonFile):
        super().__init__()
        self.cache = cache
        self.info = info

    def missing(self, key: str) -> FileSystemPath:
        if not key.startswith("assets/"):
            raise KeyError(key)

        try:
            object_hash: str = self.info.data["objects"][key[7:]]["hash"]
        except KeyError as exc:
            raise KeyError(key) from exc

        path = self.cache.directory / "objects" / object_hash[:2] / object_hash

        if not path.is_file():
            path.parent.mkdir(parents=True, exist_ok=True)
            self.cache.download(
                f"{RESOURCES_URL}/{object_hash[:2]}/{object_hash}",
                path,
            )

        return path

    def __iter__(self) -> Iterator[str]:
        for key in self.info.data["objects"]:
            yield f"assets/{key}"

    def __len__(self) -> int:
        return len(self.info.data["objects"])


class Release:
    """Class holding information about a minecraft release."""

    cache: Cache
    info: JsonFile

    _client_jar: Optional[ClientJar]
    _object_mapping: Optional[UnveilMapping]

    def __init__(self, cache: Cache, info: JsonFile):
        self.cache = cache
        self.info = info
        self._client_jar = None
        self._object_mapping = None

    @property
    def type(self) -> str:
        return self.info.data["type"]

    @property
    def client_jar(self) -> ClientJar:
        if not self._client_jar:
            path = self.cache.download(self.info.data["downloads"]["client"]["url"])
            self._client_jar = ClientJar(self.cache, path)
        return self._client_jar

    @property
    def object_mapping(self) -> UnveilMapping:
        if not self._object_mapping:
            path = self.cache.download(self.info.data["assetIndex"]["url"])
            self._object_mapping = UnveilMapping(
                AssetIndex(self.cache, JsonFile(source_path=path))
            )
        return self._object_mapping

    def mount(
        self,
        prefix: Optional[str] = None,
        fetch_objects: bool = False,
    ) -> ClientJar:
        return self.client_jar.mount(
            prefix=prefix,
            object_mapping=self.object_mapping if fetch_objects else None,
        )

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

    def mount(
        self,
        prefix: Optional[str] = None,
        fetch_objects: bool = False,
    ) -> ClientJar:
        return self.releases[self.minecraft_version].mount(prefix, fetch_objects)

    @property
    def assets(self) -> ResourcePack:
        return self.releases[self.minecraft_version].assets

    @property
    def data(self) -> DataPack:
        return self.releases[self.minecraft_version].data
