__all__ = [
    "ErrorMessage",
    "Project",
]


from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Any,
    ChainMap,
    Iterable,
    Iterator,
    List,
    MutableMapping,
    Optional,
    Sequence,
)

from beet.core.cache import MultiCache
from beet.core.utils import FileSystemPath
from beet.core.watch import DirectoryWatcher, FileChanges

from .config import ProjectConfig, load_config, locate_config
from .utils import locate_minecraft


class ErrorMessage(Exception):
    """Exception used to display nice error messages when something goes wrong."""


@dataclass
class Project:
    """Class for interacting with a beet project."""

    parent: Optional["Project"] = None

    resolved_config: Optional[ProjectConfig] = None
    config_directory: Optional[FileSystemPath] = None
    config_path: Optional[FileSystemPath] = None
    config_name: str = "beet.json"

    resolved_cache: Optional[MultiCache] = None
    cache_name: str = ".beet_cache"

    resolved_meta: Optional[MutableMapping[str, Any]] = None

    @property
    def config(self) -> ProjectConfig:
        if self.resolved_config is not None:
            return self.resolved_config
        path = (
            self.config_path
            or (self.config_directory and Path(self.config_directory, self.config_name))
            or locate_config(Path.cwd(), self.config_name)
        )
        if not path:
            raise ErrorMessage("Couldn't locate config file.")
        self.resolved_config = load_config(Path(path).resolve())
        return self.resolved_config

    @property
    def directory(self) -> Path:
        return Path(self.config.directory)

    @property
    def output(self) -> Optional[Path]:
        return self.directory / self.config.output if self.config.output else None

    @property
    def cache(self) -> MultiCache:
        if self.resolved_cache is not None:
            return self.resolved_cache
        if self.parent is None:
            self.resolved_cache = MultiCache(self.directory / self.cache_name)
        else:
            self.resolved_cache = self.parent.cache
        return self.resolved_cache

    @property
    def meta(self) -> MutableMapping[str, Any]:
        if self.resolved_meta is not None:
            return self.resolved_meta
        if self.parent is None:
            self.resolved_meta = deepcopy(self.config.meta)
        else:
            self.resolved_meta = ChainMap(deepcopy(self.config.meta), self.parent.meta)
        return self.resolved_meta

    @property
    def ignore(self) -> List[str]:
        return (
            self.config.ignore
            + ([] if self.parent is None else self.parent.ignore)
            + ([] if self.output is None else [f"/{self.output}"])
        )

    def reset(self):
        """Clear the cached config and force subsequent operations to load it again."""
        self.resolved_config = None
        self.resolved_cache = None
        self.resolved_meta = None

    def build(self):
        """Build the project."""

    def watch(self, interval: float = 0.6) -> Iterator[FileChanges]:
        """Watch the project."""
        for changes in DirectoryWatcher(
            self.directory,
            interval,
            ignore_file=".gitignore",
            ignore_patterns=[f"/{self.cache.path}", "*.tmp", ".*", *self.ignore],
        ):
            self.reset()
            yield changes

    def inspect_cache(self, patterns: Sequence[str] = ()) -> Iterable[str]:
        """Return a detailed representation for each matching cache."""
        self.cache.preload()
        keys = self.cache.match(*patterns) if patterns else self.cache.keys()
        return [str(self.cache[key]) for key in keys]

    def clear_cache(self, patterns: Sequence[str] = ()) -> Iterable[str]:
        """Clear and return the name of each matching cache."""
        with self.cache:
            self.cache.preload()
            keys = self.cache.match(*patterns) if patterns else list(self.cache.keys())
            for key in keys:
                del self.cache[key]
            return keys

    def link(self, target: Optional[FileSystemPath] = None) -> Iterable[str]:
        """Associate a linked resource pack directory and data pack directory to the project."""
        minecraft = locate_minecraft()
        target_path = Path(target).resolve() if target else minecraft

        if not target_path:
            raise ErrorMessage("Couldn't locate the Minecraft folder.")

        resource_pack_path: Optional[Path] = None
        data_pack_path: Optional[Path] = None

        if (
            not target_path.is_dir()
            and target
            and Path(target).parts == (target,)
            and not (
                minecraft and (target_path := minecraft / "saves" / target).is_dir()
            )
        ):
            raise ErrorMessage(
                f"Couldn't find {str(target)!r} in the Minecraft save folder."
            )

        if (target_path / "level.dat").is_file():
            data_pack_path = target_path / "datapacks"
            target_path = target_path.parent.parent
        if (resource_packs := target_path / "resourcepacks").is_dir():
            resource_pack_path = resource_packs

        if not (resource_pack_path or data_pack_path):
            raise ErrorMessage("Couldn't establish any link with the specified target.")

        with self.cache:
            self.cache["link"].json.update(
                resource_pack=str(resource_pack_path) if resource_pack_path else None,
                data_pack=str(data_pack_path) if data_pack_path else None,
            )

        return [
            f"{title}:\n  │  destination = {pack_dir}\n"
            for title, pack_dir in [
                ("Resource pack", resource_pack_path),
                ("Data pack", data_pack_path),
            ]
            if pack_dir
        ]

    def clear_link(self):
        """Remove the linked resource pack directory and data pack directory."""
        with self.cache:
            del self.cache["link"]
