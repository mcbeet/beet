__all__ = [
    "Pipeline",
    "Plugin",
    "PluginSpec",
    "Context",
    "ContextContainer",
    "sandbox",
]


import sys
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional, Tuple, TypeVar

from beet.core.cache import MultiCache
from beet.core.container import Container
from beet.core.utils import JsonDict, TextComponent, extra_field
from beet.library.data_pack import DataPack
from beet.library.resource_pack import ResourcePack

from .pipeline import GenericPipeline, GenericPlugin, GenericPluginSpec
from .template import TemplateManager

InjectedType = TypeVar("InjectedType")

Plugin = GenericPlugin["Context"]
PluginSpec = GenericPluginSpec["Context"]


@dataclass
class Pipeline(GenericPipeline["Context"]):
    ctx: "Context"


class ContextContainer(Container[Callable[["Context"], Any], Any]):
    """Dict-like container that instantiates and holds objects injected into the context."""

    def __init__(self, ctx: "Context"):
        super().__init__()
        self.ctx = ctx

    def missing(self, key: Callable[["Context"], Any]) -> Any:
        return key(self.ctx)


@dataclass
class Context:
    """The build context."""

    project_name: str
    project_description: TextComponent
    project_author: str
    project_version: str

    directory: Path
    output_directory: Optional[Path]
    meta: JsonDict
    cache: MultiCache
    template: TemplateManager

    assets: ResourcePack = field(default_factory=ResourcePack)
    data: DataPack = field(default_factory=DataPack)

    _container: ContextContainer = extra_field(init=False)
    _path_entry: str = extra_field(init=False)

    def __post_init__(self):
        self._container = ContextContainer(self)
        self._path_entry = str(self.directory.resolve())
        self.template.env.globals["ctx"] = self

    def inject(self, cls: Callable[["Context"], InjectedType]) -> InjectedType:
        """Retrieve the instance provided by the specified service factory."""
        return self._container[cls]

    @contextmanager
    def activate(self):
        sys.path.append(self._path_entry)

        try:
            with self.cache:
                yield self.inject(Pipeline)
        finally:
            sys.path.remove(self._path_entry)

            imported_modules = [
                name
                for name, module in sys.modules.items()
                if (filename := getattr(module, "__file__", None))
                and filename.startswith(self._path_entry)
            ]

            for name in imported_modules:
                del sys.modules[name]

    @property
    def packs(self) -> Tuple[ResourcePack, DataPack]:
        return self.assets, self.data

    def require(self, spec: PluginSpec):
        """Execute the specified plugin."""
        self.inject(Pipeline).require(spec)


def sandbox(*specs: PluginSpec) -> Plugin:
    """Return a plugin that runs the specified plugins in an isolated pipeline."""

    def plugin(ctx: Context):
        child_ctx = Context(
            project_name=ctx.project_name,
            project_description=ctx.project_description,
            project_author=ctx.project_author,
            project_version=ctx.project_version,
            directory=ctx.directory,
            output_directory=None,
            meta={},
            cache=ctx.cache,
            template=TemplateManager(
                templates=list(ctx.template.directories),
                cache_dir=ctx.cache["template"].directory,
            ),
        )

        with child_ctx.activate() as pipeline:
            pipeline.run(specs)

        ctx.assets.extra.merge(child_ctx.assets.extra)
        ctx.assets.merge(child_ctx.assets)

        ctx.data.extra.merge(child_ctx.data.extra)
        ctx.data.merge(child_ctx.data)

    return plugin
