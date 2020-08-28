__all__ = ["Project", "Context", "Generator"]


import sys
import json
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple, Union, Sequence, Iterator, Callable, Set, List

from .assets import ResourcePack
from .data import DataPack
from .utils import FileSystemPath, hidden_field, import_from_string


Generator = Callable[["Context"], None]


class Context(NamedTuple):
    project: "Project"
    directory: Path
    meta: dict
    assets: ResourcePack
    data: DataPack
    applied_generators: Set[Generator]

    DEFAULT_GENERATOR = "default_beet_generator"

    def apply(self, generator: Union[Generator, str]):
        func: Generator = (
            import_from_string(generator, default_member=self.DEFAULT_GENERATOR)
            if isinstance(generator, str)
            else generator
        )
        if func not in self.applied_generators:
            func(self)
            self.applied_generators.add(func)


@dataclass
class Project:
    name: str
    description: str
    author: str
    version: str

    directory: FileSystemPath
    generators: Sequence[Union[Generator, str]]
    meta: dict

    resource_pack_name: str = hidden_field(default="{name} Resource Pack")
    resource_pack_format: int = hidden_field(default=ResourcePack.LATEST_PACK_FORMAT)
    resource_pack_description: str = hidden_field(
        default="{description}\n\nVersion {version}\nBy {author}",
    )

    data_pack_name: str = hidden_field(default="{name}")
    data_pack_format: int = hidden_field(default=DataPack.LATEST_PACK_FORMAT)
    data_pack_description: str = hidden_field(
        default="{description}\n\nVersion {version}\nBy {author}",
    )

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
            yield Context(
                project=self,
                directory=project_path,
                meta=self.meta,
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
                applied_generators=set(),
            )
        finally:
            sys.path.remove(path_entry)

    def run_generators(self) -> Context:
        with self.context() as ctx:
            for generator in self.generators:
                ctx.apply(generator)
            return ctx

    def build(self) -> List[Union[ResourcePack, DataPack]]:
        ctx = self.run_generators()
        return [pack for pack in [ctx.assets, ctx.data] if pack]
