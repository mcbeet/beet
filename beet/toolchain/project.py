__all__ = [
    "ErrorMessage",
    "Project",
    "ProjectBuilder",
]


import re
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, List, Optional, Sequence

from beet.core.cache import MultiCache
from beet.core.utils import FileSystemPath
from beet.core.watch import DirectoryWatcher, FileChanges

from .config import (
    InvalidProjectConfig,
    PackConfig,
    ProjectConfig,
    load_config,
    locate_config,
)
from .context import Context, Pipeline
from .pipeline import PluginError
from .template import TemplateError, TemplateManager
from .utils import locate_minecraft


class ErrorMessage(Exception):
    """Exception used to display nice error messages when something goes wrong."""


@dataclass
class Project:
    """Class for interacting with a beet project."""

    resolved_config: Optional[ProjectConfig] = None
    config_directory: Optional[FileSystemPath] = None
    config_path: Optional[FileSystemPath] = None
    config_name: str = "beet.json"

    resolved_cache: Optional[MultiCache] = None
    cache_name: str = ".beet_cache"

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
    def output_directory(self) -> Optional[Path]:
        return self.directory / self.config.output if self.config.output else None

    @property
    def template_directories(self) -> List[FileSystemPath]:
        return [
            self.directory / directory
            for directory in (self.config.templates or ["templates"])
        ]

    @property
    def cache(self) -> MultiCache:
        if self.resolved_cache is not None:
            return self.resolved_cache
        self.resolved_cache = MultiCache(self.directory / self.cache_name)
        return self.resolved_cache

    @property
    def ignore(self) -> List[str]:
        ignore = list(self.config.ignore)
        if self.output_directory:
            ignore.append(f"{self.output_directory.relative_to(self.directory)}/")
        return ignore

    def reset(self):
        """Clear the cached config and force subsequent operations to load it again."""
        self.resolved_config = None
        self.resolved_cache = None

    def build(self):
        """Build the project."""
        ctx = ProjectBuilder(self).build()

        for link_key, pack in zip(["resource_pack", "data_pack"], ctx.packs):
            if pack and (link_dir := ctx.cache["link"].json.get(link_key)):
                pack.save(link_dir, overwrite=True)

    def watch(self, interval: float = 0.6) -> Iterator[FileChanges]:
        """Watch the project."""
        for changes in DirectoryWatcher(
            self.directory,
            interval,
            ignore_file=".gitignore",
            ignore_patterns=[
                f"{self.cache.path.relative_to(self.directory)}/",
                "__pycache__/",
                "*.tmp",
                ".*",
                *self.ignore,
            ],
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


class ProjectBuilder:
    """Class capable of building a project."""

    project: Project
    config: ProjectConfig

    def __init__(self, project: Project):
        self.project = project
        self.config = self.project.config

    def build(self) -> Context:
        """Create the context, run the pipeline, and return the context."""
        ctx = Context(
            directory=self.project.directory,
            output_directory=self.project.output_directory,
            meta=deepcopy(self.config.meta),
            cache=self.project.cache,
            template=TemplateManager(
                templates=self.project.template_directories,
                cache_dir=self.project.cache["template"].directory,
            ),
        )

        ctx.template.env.globals["ctx"] = ctx

        with ctx, ctx.cache:
            pipeline = ctx.inject(Pipeline)
            pipeline.exception_fallthrough = (
                ErrorMessage,
                InvalidProjectConfig,
                PluginError,
                TemplateError,
            )

            pipeline.require(self.bootstrap)

            pipeline.run(
                (
                    item
                    if isinstance(item, str)
                    else ProjectBuilder(
                        Project(resolved_config=item, resolved_cache=ctx.cache)
                    )
                )
                for item in self.config.pipeline
            )

        return ctx

    def bootstrap(self, ctx: Context):
        """Plugin that handles the project configuration."""
        for plugin in self.config.require:
            ctx.require(plugin)

        pack_configs = [self.config.resource_pack, self.config.data_pack]

        for config, pack in zip(pack_configs, ctx.packs):
            for path in config.load:
                pack.load(path)

        for config, pack in zip(pack_configs, ctx.packs):
            for group, patterns in config.render.items():
                try:
                    proxy = getattr(pack, group)
                    file_paths = proxy.match(*patterns)
                except:
                    message = f"Invalid pattern group {group!r} in configuration."
                    raise ErrorMessage(message) from None
                else:
                    for path in file_paths:
                        ctx.template.render_file(
                            proxy[path],
                            __render__={"path": path, "group": group},
                        )

        yield

        name = self.config.name or ctx.directory.stem
        normalized_name = re.sub(r"[^a-z0-9]+", "_", name.lower())

        description_parts = [
            self.config.description,
            self.config.author and f"Author: {self.config.author}",
            self.config.version and f"Version: {self.config.version}",
        ]
        description = "\n".join(filter(None, description_parts))

        for is_data_pack, (config, pack) in enumerate(zip(pack_configs, ctx.packs)):
            default_name = normalized_name
            if self.config.version:
                default_name += "_" + self.config.version
            default_name += "_data_pack" if is_data_pack else "_resource_pack"

            options = config.with_defaults(
                PackConfig(
                    name=default_name,
                    description=description,
                    pack_format=pack.pack_format,
                    zipped=pack.zipped,
                )
            )

            pack.name = options.name
            pack.description = options.description
            pack.pack_format = options.pack_format
            pack.zipped = bool(options.zipped)

            if pack and ctx.output_directory:
                pack.save(ctx.output_directory, overwrite=True)

    def __call__(self, ctx: Context):
        """The builder instance is itself a plugin used for merging subpipelines."""
        child_ctx = self.build()

        if child_ctx.output_directory:
            return

        ctx.assets.extra.merge(child_ctx.assets.extra)
        ctx.assets.merge(child_ctx.assets)

        ctx.data.extra.merge(child_ctx.data.extra)
        ctx.data.merge(child_ctx.data)
