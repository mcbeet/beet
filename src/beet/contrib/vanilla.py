"""Service for fetching and unpacking vanilla resources."""

__all__ = [
    "LoadVanillaOptions",
    "load_vanilla",
    "Vanilla",
    "VanillaOptions",
    "ReleaseRegistry",
    "Release",
    "ClientJar",
    "AssetIndex",
    "MANIFEST_URL",
    "RESOURCES_URL",
]


import os
import re
from pathlib import Path
import stat
from typing import Iterator, Optional, Union
from zipfile import ZipFile
from platform import system, machine
from beet import (
    LATEST_MINECRAFT_VERSION,
    Cache,
    Container,
    Context,
    DataPack,
    JsonFile,
    PackFilesOption,
    PackMatchOption,
    PluginOptions,
    ResourcePack,
    UnveilMapping,
    configurable,
)
from beet.contrib.worldgen import worldgen
from beet.core.utils import FileSystemPath, JsonDict, log_time_scope

MANIFEST_URL: str = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
RESOURCES_URL: str = "https://resources.download.minecraft.net"
RUNTIMES_URL: str = "https://launchermeta.mojang.com/v1/products/java-runtime/2ec0cc96c44e5a76b9c8b7c39df7210883d12871/all.json"


class VanillaOptions(PluginOptions):
    version: Optional[str] = None
    manifest: Optional[str] = None
    runtimes: str | None = None


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
            with log_time_scope("Extract vanilla pack."):
                pack.load(ZipFile(self.path))
                pack.save(path=path)
        elif pack.path != path.parent:
            if pack.unveil(prefix, path):
                pack.mount(prefix, path / prefix)

        if object_mapping and isinstance(pack, ResourcePack):
            if pack.unveil(prefix, object_mapping):
                # Download into an empty resource pack first to avoid
                # triggering merge policies that might try to deserialize
                # files before they're fully retrieved.
                temp = ResourcePack()
                with self.cache.parallel_downloads():
                    temp.mount(prefix, object_mapping.with_prefix(prefix))
                pack.merge(temp)

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


class ServerJar:
    """Class holding information about a server jar."""

    cache: Cache
    path: Path

    def __init__(self, cache: Cache, path: FileSystemPath):
        self.cache = cache
        self.path = Path(path)


class Release:
    """Class holding information about a minecraft release."""

    cache: Cache
    info: JsonFile

    _client_jar: Optional[ClientJar]
    _server_jar: Optional[ServerJar]
    _object_mapping: Optional[UnveilMapping]

    def __init__(self, cache: Cache, info: JsonFile):
        self.cache = cache
        self.info = info
        self._client_jar = None
        self._server_jar = None
        self._object_mapping = None

    @property
    def type(self) -> str:
        return self.info.data["type"]

    @property
    def runtime(self) -> str:
        return self.info.data["javaVersion"]["component"]

    @property
    def client_jar(self) -> ClientJar:
        if not self._client_jar:
            path = self.cache.download(self.info.data["downloads"]["client"]["url"])
            self._client_jar = ClientJar(self.cache, path)
        return self._client_jar

    @property
    def server_jar(self) -> ServerJar:
        if not self._server_jar:
            path = self.cache.download(self.info.data["downloads"]["server"]["url"])
            self._server_jar = ServerJar(self.cache, path)
        return self._server_jar

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
        pattern = re.compile(
            "^"
            + "|".join(
                r"\d+".join(map(re.escape, k.split("*")))
                for k in [key, key.removesuffix(".*")]
            )
            + "$"
        )
        for version in self.manifest.data["versions"]:
            if pattern.match(version["id"]):
                info = JsonFile(source_path=self.cache.download(version["url"]))
                return Release(self.cache, info)
        raise KeyError(key)


class Runtime:
    """Class holding information about a minecraft runtime."""

    cache: Cache
    info: JsonFile
    component: str

    _java: Path | None

    def __init__(self, cache: Cache, info: JsonFile, component: str):
        self.cache = cache
        self.info = info
        self.component = component
        self._java = None

    @property
    def java(self) -> Path:
        if not self._java:
            dest = self.cache.directory / self.component
            files: JsonDict = self.info.data["files"]
            is_windows = system() == "Windows"

            dest.mkdir(exist_ok=True)

            with self.cache.parallel_downloads():
                self.download_files(dest, files, is_windows)

            java = "bin/java.exe" if is_windows else "bin/java"
            self._java = dest / next(path for path in files if path.endswith(java))

        return self._java

    @property
    def javaw(self) -> Path:
        return self.java.with_name("javaw.exe")

    def download_files(self, dest: Path, files: JsonDict, is_windows: bool):
        for path, meta in sorted(files.items()):
            target = dest / path
            entry_type = meta["type"]

            if entry_type == "directory":
                target.mkdir(exist_ok=True)

            elif entry_type == "link":
                if is_windows:
                    continue
                link_target = meta["target"]
                if link_target:
                    if target.exists() or target.is_symlink():
                        target.unlink()
                    os.symlink(link_target, target)

            elif entry_type == "file":
                self.cache.download(meta["downloads"]["raw"]["url"], target)
                if meta["executable"] and not is_windows:
                    current = target.stat().st_mode
                    target.chmod(current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


class RuntimeRegistry(Container[str, Runtime]):
    """Registry for minecraft runtimes."""

    cache: Cache
    manifest: JsonFile
    platform: str

    def __init__(
        self,
        cache: Cache,
        manifest: FileSystemPath | JsonFile | None = None,
        platform: str = "",
    ):
        super().__init__()
        self.cache = cache

        manifest = manifest or RUNTIMES_URL

        if isinstance(manifest, str) and manifest.startswith(("http://", "https://")):
            manifest = self.cache.download(manifest)
        if not isinstance(manifest, JsonFile):
            manifest = JsonFile(source_path=manifest)

        if not platform:
            current_system = system()
            current_machine = machine().lower()

            if current_system == "Linux":
                if current_machine in ("i386", "i686", "x86"):
                    platform = "linux-i386"
                else:
                    platform = "linux"
            elif current_system == "Darwin":
                if current_machine in ("arm64", "aarch64"):
                    platform = "mac-os-arm64"
                else:
                    platform = "mac-os"
            elif current_system == "Windows":
                if current_machine in ("arm64", "aarch64"):
                    platform = "windows-arm64"
                elif current_machine in ("amd64", "x86_64"):
                    platform = "windows-x64"
                else:
                    platform = "windows-x86"

        self.manifest = manifest
        self.platform = platform

    def missing(self, key: str) -> Runtime:
        if components := self.manifest.data.get(self.platform):
            for component in components.get(key, []):
                url = component["manifest"]["url"]
                info = JsonFile(source_path=self.cache.download(url))
                return Runtime(self.cache, info, key)
        raise KeyError(key)


class Vanilla:
    """Service for fetching and unpacking vanilla resources."""

    cache: Cache
    releases: ReleaseRegistry
    runtimes: RuntimeRegistry
    minecraft_version: str

    def __init__(
        self,
        ctx: Optional[Context] = None,
        *,
        cache: Optional[Cache] = None,
        manifest: Optional[Union[FileSystemPath, JsonFile]] = None,
        runtimes: Optional[Union[FileSystemPath, JsonFile]] = None,
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
        self.runtimes = RuntimeRegistry(self.cache, runtimes or opts and opts.runtimes)

        if minecraft_version:
            self.minecraft_version = minecraft_version
        elif opts and opts.version:
            self.minecraft_version = opts.version
        elif ctx:
            self.minecraft_version = f"{ctx.minecraft_version}.*"
        else:
            self.minecraft_version = f"{LATEST_MINECRAFT_VERSION}.*"

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

    @property
    def client(self) -> Path:
        return self.releases[self.minecraft_version].client_jar.path

    @property
    def server(self) -> Path:
        return self.releases[self.minecraft_version].server_jar.path

    @property
    def java(self) -> Path:
        component = self.releases[self.minecraft_version].runtime
        return self.runtimes[component].java

    @property
    def javaw(self) -> Path:
        component = self.releases[self.minecraft_version].runtime
        return self.runtimes[component].javaw


class LoadVanillaOptions(PluginOptions):
    version: Optional[str] = None
    files: PackFilesOption = PackFilesOption()
    match: PackMatchOption = PackMatchOption()


@configurable(validator=LoadVanillaOptions)
def load_vanilla(ctx: Context, opts: LoadVanillaOptions):
    vanilla = ctx.inject(Vanilla)
    release = vanilla.releases[opts.version or vanilla.minecraft_version]
    client_jar = release.client_jar

    query = ctx.query.from_pack(client_jar.assets, client_jar.data).prepare(
        [opts.files, opts.match]
    )

    for base_path in query.analyze_base_paths():
        release.mount(base_path, fetch_objects=True)

    query.copy_to(ctx.packs)
