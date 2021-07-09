__all__ = [
    "ErrorMessage",
    "Project",
    "ProjectBuilder",
]


from copy import deepcopy
from dataclasses import dataclass
from glob import glob
from importlib.metadata import entry_points
from pathlib import Path
from typing import ClassVar, Iterable, Iterator, List, Optional, Sequence

from beet.contrib.render import render
from beet.core.utils import FileSystemPath, intersperse, normalize_string
from beet.core.watch import DirectoryWatcher, FileChanges

from .config import PackConfig, ProjectConfig, load_config, locate_config
from .context import Context, ProjectCache
from .pipeline import FormattedPipelineException
from .template import TemplateManager
from .utils import locate_minecraft
from .worker import WorkerPool


class ErrorMessage(FormattedPipelineException):
    """Exception used to display nice error messages when something goes wrong."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


@dataclass
class Project:
    """Class for interacting with a beet project."""

    resolved_config: Optional[ProjectConfig] = None
    config_directory: Optional[FileSystemPath] = None
    config_path: Optional[FileSystemPath] = None
    config_detect: Iterable[str] = (
        "beet.json",
        "beet.toml",
        "beet.yml",
        "beet.yaml",
        "pyproject.toml",
    )

    resolved_cache: Optional[ProjectCache] = None
    cache_name: str = ".beet_cache"

    resolved_worker_pool: Optional[WorkerPool] = None

    @property
    def config(self) -> ProjectConfig:
        if self.resolved_config is not None:
            return self.resolved_config

        if self.config_path:
            paths = [self.config_path]
        elif self.config_directory:
            paths = [
                path
                for filename in self.config_detect
                if (path := Path(self.config_directory, filename)).is_file()
            ]
        else:
            paths = locate_config(Path.cwd(), *self.config_detect)

        if not paths:
            raise ErrorMessage("Couldn't locate config file.")

        self.resolved_config = load_config(Path(paths[0]).resolve())
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
    def cache(self) -> ProjectCache:
        if self.resolved_cache is not None:
            return self.resolved_cache
        self.resolved_cache = ProjectCache(
            self.directory / self.cache_name, self.directory / "generated"
        )
        return self.resolved_cache

    @property
    def ignore(self) -> List[str]:
        ignore = list(self.config.ignore)
        if self.output_directory:
            ignore.append(f"{self.output_directory.relative_to(self.directory)}/")
        return ignore

    @property
    def worker_pool(self):
        if self.resolved_worker_pool is not None:
            return self.resolved_worker_pool
        self.resolved_worker_pool = WorkerPool()
        return self.resolved_worker_pool

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
        with self.worker_pool.long_lived_session():
            for changes in DirectoryWatcher(
                self.directory,
                interval,
                ignore_file=".gitignore",
                ignore_patterns=[
                    f"{self.cache.path.relative_to(self.directory.resolve())}/",
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

    autoload: ClassVar[Optional[List[str]]] = None

    def __init__(self, project: Project):
        self.project = project
        self.config = self.project.config

        if ProjectBuilder.autoload is None:
            ProjectBuilder.autoload = [
                ep.value
                for ep in entry_points().get("beet", ())
                if ep.name == "autoload"
            ]

    def build(self) -> Context:
        """Create the context, run the pipeline, and return the context."""
        name = self.config.name or self.project.directory.stem

        with self.project.worker_pool.handle() as worker_pool_handle:
            ctx = Context(
                project_id=self.config.id or normalize_string(name),
                project_name=name,
                project_description=self.config.description,
                project_author=self.config.author,
                project_version=self.config.version,
                directory=self.project.directory,
                output_directory=self.project.output_directory,
                meta=deepcopy(self.config.meta),
                cache=self.project.cache,
                worker=worker_pool_handle,
                template=TemplateManager(
                    templates=self.project.template_directories,
                    cache_dir=self.project.cache["template"].directory,
                ),
                whitelist=self.config.whitelist,
            )

            with ctx.activate() as pipeline:
                pipeline.require(self.bootstrap)
                pipeline.run(
                    (
                        item
                        if isinstance(item, str)
                        else ProjectBuilder(
                            Project(
                                resolved_config=item,
                                resolved_cache=ctx.cache,
                                resolved_worker_pool=self.project.worker_pool,
                            )
                        )
                    )
                    for item in self.config.pipeline
                )

        return ctx

    def bootstrap(self, ctx: Context):
        """Plugin that handles the project configuration."""
        plugins = (self.autoload or []) + self.config.require

        for plugin in plugins:
            ctx.require(plugin)

        pack_configs = [self.config.resource_pack, self.config.data_pack]
        pack_suffixes = ["_resource_pack", "_data_pack"]

        for config, pack in zip(pack_configs, ctx.packs):
            for pattern in config.load:
                for path in glob(pattern):
                    pack.load(path)

        ctx.require(
            render(
                resource_pack=self.config.resource_pack.render,
                data_pack=self.config.data_pack.render,
            )
        )

        yield

        description_parts = [
            ctx.project_description if isinstance(ctx.project_description, str) else "",
            ctx.project_author and f"Author: {ctx.project_author}",
            ctx.project_version and f"Version: {ctx.project_version}",
        ]

        description = "\n".join(filter(None, description_parts))
        if not isinstance(ctx.project_description, str):
            description = list(
                intersperse(filter(None, [ctx.project_description, description]), "\n")
            )

        for config, suffix, pack in zip(pack_configs, pack_suffixes, ctx.packs):
            default_name = ctx.project_id
            if ctx.project_version:
                default_name += "_" + ctx.project_version
            default_name += suffix

            config = config.with_defaults(
                PackConfig(
                    name=default_name,
                    description=pack.description or description,
                    pack_format=pack.pack_format,
                    zipped=pack.zipped,
                )
            )

            pack.name = ctx.template.render_string(config.name)
            pack.description = ctx.template.render_json(config.description)
            pack.pack_format = config.pack_format
            pack.zipped = bool(config.zipped)

            if pack and ctx.output_directory:
                pack.save(ctx.output_directory, overwrite=True)

    def __call__(self, ctx: Context):
        """The builder instance is itself a plugin used for merging subpipelines."""
        child_ctx = self.build()

        if child_ctx.output_directory:
            return

        ctx.assets.merge(child_ctx.assets)
        ctx.data.merge(child_ctx.data)
