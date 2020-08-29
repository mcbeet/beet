__all__ = ["Project", "Context", "Generator"]


import sys
import json
from contextlib import contextmanager
from collections import deque
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple, Union, Sequence, Iterator, Callable, Set, List, Deque

from .assets import ResourcePack
from .data import DataPack
from .cache import MultiCache
from .utils import FileSystemPath, extra_field, import_from_string


Generator = Callable[["Context"], None]
GeneratorSpec = Union[Generator, str]


class Context(NamedTuple):
    directory: Path
    meta: dict
    cache: MultiCache
    assets: ResourcePack
    data: DataPack
    queue: Deque[GeneratorSpec]
    applied_generators: Set[Generator]

    DEFAULT_GENERATOR = "default_beet_generator"

    def apply(self, generator: GeneratorSpec):
        func: Generator = (
            import_from_string(generator, default_member=self.DEFAULT_GENERATOR)
            if isinstance(generator, str)
            else generator
        )
        if func not in self.applied_generators:
            self.applied_generators.add(func)
            func(self)


@dataclass
class Project:
    name: str
    description: str
    author: str
    version: str

    directory: FileSystemPath
    generators: Sequence[GeneratorSpec]
    meta: dict

    resource_pack_name: str = extra_field(default="{name} Resource Pack")
    resource_pack_format: int = extra_field(default=ResourcePack.LATEST_PACK_FORMAT)
    resource_pack_description: str = extra_field(
        default="{description}\n\nVersion {version}\nBy {author}",
    )

    data_pack_name: str = extra_field(default="{name}")
    data_pack_format: int = extra_field(default=DataPack.LATEST_PACK_FORMAT)
    data_pack_description: str = extra_field(
        default="{description}\n\nVersion {version}\nBy {author}",
    )

    CACHE_DIRECTORY = ".beet_cache"

    @classmethod
    def from_config(cls, config_file: FileSystemPath) -> "Project":
        config_path = Path(config_file).absolute()

        config = json.loads(config_path.read_text())
        meta = config.get("meta", {})

        return cls(
            name=config.get("name", "Untitled"),
            description=config.get("description", ""),
            author=config.get("author", "Unknown"),
            version=config.get("version", "0.0.0"),
            directory=config_path.parent,
            generators=config.get("generators", []),
            meta=meta,
            **{
                key: value
                for key in [
                    "resource_pack_name",
                    "resource_pack_format",
                    "resource_pack_description",
                    "data_pack_name",
                    "data_pack_format",
                    "data_pack_description",
                ]
                if (value := meta.get(key))
            },
        )

    @contextmanager
    def context(self) -> Iterator[Context]:
        project_path = Path(self.directory).absolute()
        path_entry = str(project_path)

        variables = {
            "name": self.name,
            "description": self.description,
            "author": self.author,
            "version": self.version,
        }

        sys.path.append(path_entry)

        try:
            with MultiCache(project_path / self.CACHE_DIRECTORY) as cache:
                yield Context(
                    directory=project_path,
                    meta=deepcopy(self.meta),
                    cache=cache,
                    assets=ResourcePack(
                        self.resource_pack_name.format_map(variables),
                        self.resource_pack_description.format_map(variables),
                        self.resource_pack_format,
                    ),
                    data=DataPack(
                        self.data_pack_name.format_map(variables),
                        self.data_pack_description.format_map(variables),
                        self.data_pack_format,
                    ),
                    queue=deque(self.generators),
                    applied_generators=set(),
                )
        finally:
            sys.path.remove(path_entry)

            imported_modules = [
                name
                for name, module in sys.modules.items()
                if getattr(module, "__file__", "").startswith(path_entry)
            ]

            for name in imported_modules:
                del sys.modules[name]

    def build(self) -> Context:
        with self.context() as ctx:
            while ctx.queue:
                ctx.apply(ctx.queue.popleft())
            return ctx
