__all__ = [
    "Pipeline",
    "Plugin",
    "PluginSpec",
    "Context",
    "ContextContainer",
]


import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional, Tuple, TypeVar

from beet.core.cache import MultiCache
from beet.core.container import Container
from beet.core.utils import JsonDict, extra_field
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

    def inject(self, cls: Callable[["Context"], InjectedType]) -> InjectedType:
        return self._container[cls]

    def __enter__(self) -> "Context":
        sys.path.append(self._path_entry)
        return self

    def __exit__(self, *_):
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
