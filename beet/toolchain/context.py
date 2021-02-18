__all__ = [
    "Pipeline",
    "Plugin",
    "PluginSpec",
    "Context",
    "ContextContainer",
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
        """Push the context directory to sys.path and handle cleanup to allow module reloading."""
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

    @contextmanager
    def override(self, **meta: Any):
        """Temporarily update the context meta."""
        to_restore = {}
        to_remove = set()

        for key, value in meta.items():
            if key in self.meta:
                to_restore[key] = self.meta[key]
            else:
                to_remove.add(key)
            self.meta[key] = value

        try:
            yield self
        finally:
            for key in to_remove:
                del self.meta[key]
            self.meta.update(to_restore)

    @property
    def packs(self) -> Tuple[ResourcePack, DataPack]:
        return self.assets, self.data

    def require(self, spec: PluginSpec):
        """Execute the specified plugin."""
        self.inject(Pipeline).require(spec)
