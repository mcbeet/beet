__all__ = [
    "ProjectConfig",
    "PackConfig",
    "load_config",
]


import json
from copy import deepcopy
from pathlib import Path
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field

from beet.core.utils import FileSystemPath, JsonDict


class PackConfig(BaseModel):
    """Data pack and resource pack configuration."""

    name: str = ""
    description: str = ""
    pack_format: int = 0
    zipped: Optional[bool] = None

    load: List[str] = Field(default_factory=list)
    render: Dict[str, List[str]] = Field(default_factory=dict)

    class Config:
        extra = "forbid"

    def with_defaults(self, other: "PackConfig") -> "PackConfig":
        """Combine the current pack config with another one."""
        return PackConfig(
            name=self.name or other.name,
            description=self.description or other.description,
            pack_format=self.pack_format or other.pack_format,
            zipped=other.zipped if self.zipped is None else self.zipped,
            load=other.load + self.load,
            render={
                key: other.render.get(key, []) + self.render.get(key, [])
                for key in self.render.keys() | other.render.keys()
            },
        )


class ProjectConfig(BaseModel):
    """Beet project configuration."""

    name: str = ""
    description: str = ""
    author: str = ""
    version: str = ""

    directory: str = ""
    extend: List[str] = Field(default_factory=list)
    output: str = ""
    ignore: List[str] = Field(default_factory=list)
    cache: str = ""

    require: List[str] = Field(default_factory=list)
    templates: List[str] = Field(default_factory=list)
    data_pack: PackConfig = Field(default_factory=PackConfig)
    resource_pack: PackConfig = Field(default_factory=PackConfig)
    pipeline: List[Union[str, "ProjectConfig"]] = Field(default_factory=list)
    meta: JsonDict = Field(default_factory=dict)

    class Config:
        extra = "forbid"

    def resolve(self, directory: FileSystemPath) -> "ProjectConfig":
        """Resolve paths relative to the given directory and apply inheritance."""
        path = Path(directory)

        if self.directory:
            path /= self.directory

        self.directory = str(path)

        if self.output:
            self.output = str(path / self.output)
        if self.cache:
            self.cache = str(path / self.cache)

        self.templates = [str(path / template_path) for template_path in self.templates]

        self.data_pack.load = [
            str(path / data_pack_path) for data_pack_path in self.data_pack.load
        ]

        self.resource_pack.load = [
            str(path / resource_pack_path)
            for resource_pack_path in self.resource_pack.load
        ]

        self.pipeline = [
            item.resolve(path) if isinstance(item, ProjectConfig) else item
            for item in self.pipeline
        ]

        while self.extend:
            self = self.with_defaults(load_config(path / self.extend.pop()))

        return self

    def with_defaults(self, other: "ProjectConfig") -> "ProjectConfig":
        """Combine the current project config with another one."""
        return ProjectConfig(
            name=self.name or other.name,
            description=self.description or other.description,
            author=self.author or other.author,
            version=self.version or other.version,
            directory=self.directory,
            extend=self.extend,
            output=self.output or other.output,
            ignore=other.ignore + self.ignore,
            cache=other.cache + self.cache,
            data_pack=self.data_pack.with_defaults(other.data_pack),
            resource_pack=self.resource_pack.with_defaults(other.resource_pack),
            templates=other.templates + self.templates,
            require=other.require + self.require,
            pipeline=other.pipeline + self.pipeline,
            meta={**deepcopy(other.meta), **deepcopy(self.meta)},
        )


ProjectConfig.update_forward_refs()


def load_config(filename: FileSystemPath) -> ProjectConfig:
    """Load the project config at the specified location."""
    path = Path(filename)
    return ProjectConfig(**json.loads(path.read_text())).resolve(path.parent)
