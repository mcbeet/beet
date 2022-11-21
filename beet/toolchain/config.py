__all__ = [
    "ProjectConfig",
    "PackConfig",
    "PackFilterBlockConfig",
    "PackFilterConfig",
    "PackLoadOptions",
    "ListOption",
    "PackageablePath",
    "InvalidProjectConfig",
    "locate_config",
    "load_config",
    "config_error_handler",
    "DETECT_CONFIG_FILES",
]


import json
from contextlib import contextmanager, nullcontext
from copy import deepcopy
from glob import glob
from itertools import chain
from pathlib import Path
from typing import Any, Dict, Generic, List, Literal, Optional, Tuple, TypeVar, Union

import toml
import yaml
from pydantic import BaseModel, ValidationError, root_validator, validator
from pydantic.generics import GenericModel

from beet.core.error import BubbleException
from beet.core.utils import (
    FileSystemPath,
    JsonDict,
    TextComponent,
    format_validation_error,
    local_import_path,
    resolve_packageable_path,
)

from .utils import apply_option, eval_option, iter_options

DETECT_CONFIG_FILES: Tuple[str, ...] = (
    "beet.json",
    "beet.toml",
    "beet.yml",
    "beet.yaml",
    "pyproject.toml",
)


class InvalidProjectConfig(BubbleException):
    """Raised when trying to load an invalid project config."""

    explanation: str

    def __init__(self, explanation: str):
        super().__init__(explanation)
        self.explanation = explanation

    def __str__(self) -> str:
        return f"Couldn't load project config.\n\n{self.explanation}"


ItemType = TypeVar("ItemType")


class ListOption(GenericModel, Generic[ItemType]):
    """List that transparently wraps single values."""

    __root__: List[ItemType] = []

    @validator("__root__", pre=True)
    def validate_root(cls, value: Any) -> Any:
        if value is None:
            value = []
        if isinstance(value, ListOption):
            value = value.entries()
        if not isinstance(value, (list, tuple)):
            value = [value]
        return value  # type: ignore

    def entries(self) -> List[ItemType]:
        """Return the internal list."""
        return self.__root__


class PackageablePath(BaseModel):
    """Path that can be resolved from a python package."""

    __root__: FileSystemPath

    @validator("__root__")
    def validate_root(cls, value: Any):
        return resolve_packageable_path(value)

    def resolve(self, directory: FileSystemPath) -> "PackageablePath":
        """Resolve path relative to the given directory."""
        return PackageablePath.parse_obj(Path(directory) / self.__root__)

    def __fspath__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return str(self.__root__)


class PackLoadOptions(
    ListOption[Union[PackageablePath, Dict[str, ListOption[PackageablePath]]]]
):
    """Options for loading data packs and resource packs."""

    def resolve(self, directory: FileSystemPath) -> "PackLoadOptions":
        """Resolve load options relative to the given directory."""
        return PackLoadOptions.parse_obj(
            [
                (
                    {
                        prefix: ListOption.parse_obj(
                            [
                                pattern.resolve(directory)
                                for pattern in mount_options.entries()
                            ]
                        )
                        for prefix, mount_options in load_entry.items()
                    }
                    if isinstance(load_entry, dict)
                    else load_entry.resolve(directory)
                )
                for load_entry in self.entries()
            ]
        )


class PackFilterBlockConfig(BaseModel):
    """Data pack and resource pack filter block configuration."""

    namespace: Optional[str] = None
    path: Optional[str] = None


class PackFilterConfig(BaseModel):
    """Data pack and resource pack filter configuration."""

    block: ListOption[PackFilterBlockConfig] = ListOption()

    def with_defaults(self, other: "PackFilterConfig") -> "PackFilterConfig":
        return PackFilterConfig.parse_obj(
            {
                "block": other.block.entries() + self.block.entries(),
            }
        )


class PackConfig(BaseModel):
    """Data pack and resource pack configuration."""

    name: str = ""
    description: TextComponent = ""
    pack_format: int = 0
    filter: Optional[PackFilterConfig] = None
    zipped: Optional[bool] = None
    compression: Optional[Literal["none", "deflate", "bzip2", "lzma"]] = None
    compression_level: Optional[int] = None

    load: PackLoadOptions = PackLoadOptions()
    render: Dict[str, ListOption[str]] = {}

    class Config:
        extra = "forbid"

    def with_defaults(self, other: "PackConfig") -> "PackConfig":
        """Combine the current pack config with another one."""
        return PackConfig.parse_obj(
            {
                "name": self.name or other.name,
                "description": self.description or other.description,
                "pack_format": self.pack_format or other.pack_format,
                "filter": (
                    self.filter.with_defaults(other.filter)
                    if self.filter and other.filter
                    else self.filter or other.filter
                ),
                "zipped": other.zipped if self.zipped is None else self.zipped,
                "compression": (
                    other.compression if self.compression is None else self.compression
                ),
                "compression_level": (
                    other.compression_level
                    if self.compression_level is None
                    else self.compression_level
                ),
                "load": other.load.entries() + self.load.entries(),
                "render": {
                    key: other.render.get(key, ListOption()).entries()
                    + self.render.get(key, ListOption()).entries()
                    for key in self.render.keys() | other.render.keys()
                },
            }
        )


class ProjectConfig(BaseModel):
    """Beet project configuration."""

    id: str = ""
    name: str = ""
    description: TextComponent = ""
    author: str = ""
    version: str = ""
    minecraft: str = ""

    directory: FileSystemPath = ""
    broadcast: ListOption[FileSystemPath] = ListOption()
    extend: ListOption[PackageablePath] = ListOption()
    output: Optional[FileSystemPath] = None
    ignore: List[str] = []
    whitelist: Optional[List[str]] = None

    require: List[str] = []
    templates: ListOption[PackageablePath] = ListOption()
    data_pack: PackConfig = PackConfig()
    resource_pack: PackConfig = PackConfig()
    pipeline: List[Union[str, "ProjectConfig"]] = []
    meta: JsonDict = {}

    class Config:
        extra = "forbid"

    @root_validator(pre=True)
    def apply_overrides(cls, values: JsonDict):
        """Apply config overrides."""
        for option in iter_options(values):
            try:
                values = apply_option(values, eval_option(option))
            except Exception:
                raise InvalidProjectConfig(
                    f"Couldn't apply override {option!r}."
                ) from None
        values.pop("overrides", None)
        return values

    def resolve(self, directory: FileSystemPath) -> "ProjectConfig":
        """Resolve paths relative to the given directory and apply inheritance."""
        path = Path(directory)

        if self.directory:
            path /= self.directory

        self.directory = path

        if broadcast := self.broadcast.entries():
            parent = ProjectConfig(meta={"autosave": {"link": False}})

            for broadcast_entry in broadcast:
                if dirs := glob(str(path / broadcast_entry)):
                    for dirname in dirs:
                        config = self.copy(
                            update={"directory": dirname, "broadcast": ListOption()},
                            deep=True,
                        )
                        config.meta.setdefault("broadcast_directory", path)
                        config.meta.setdefault("autosave", {}).setdefault("link", True)
                        parent.pipeline.append(config)
                else:
                    msg = f'Couldn\'t broadcast "{broadcast_entry}".'
                    raise InvalidProjectConfig(msg)

            return parent.resolve(directory)

        if self.output:
            self.output = path / self.output

        self.templates = ListOption.parse_obj(
            [template_path.resolve(path) for template_path in self.templates.entries()]
        )

        for pack_config in [self.data_pack, self.resource_pack]:
            pack_config.load = pack_config.load.resolve(path)

        self.pipeline = [
            item.resolve(path) if isinstance(item, ProjectConfig) else item
            for item in self.pipeline
        ]

        while extend := self.extend.entries():
            self = self.with_defaults(load_config(path / extend.pop()))

        return self

    def with_defaults(self, other: "ProjectConfig") -> "ProjectConfig":
        """Combine the current project config with another one."""
        return ProjectConfig.parse_obj(
            {
                "id": self.id or other.id,
                "name": self.name or other.name,
                "description": self.description or other.description,
                "author": self.author or other.author,
                "version": self.version or other.version,
                "minecraft": self.minecraft or other.minecraft,
                "directory": self.directory,
                "extend": self.extend,
                "output": self.output,
                "ignore": other.ignore + self.ignore,
                "data_pack": self.data_pack.with_defaults(other.data_pack),
                "resource_pack": self.resource_pack.with_defaults(other.resource_pack),
                "templates": other.templates.entries() + self.templates.entries(),
                "whitelist": (
                    self.whitelist
                    if other.whitelist is None
                    else other.whitelist + (self.whitelist or [])
                ),
                "require": other.require + self.require,
                "pipeline": other.pipeline + self.pipeline,
                "meta": {**deepcopy(other.meta), **deepcopy(self.meta)},
            }
        )


ProjectConfig.update_forward_refs()


def locate_config(directory: FileSystemPath, parents: bool = False) -> Optional[Path]:
    """Try to locate a config file in the given directory or its parents."""
    start = Path(directory).resolve()

    for directory in chain([start], start.parents if parents else []):
        for filename in DETECT_CONFIG_FILES:
            if (path := directory / filename).is_file():
                return path

    return None


def load_config(
    filename: Optional[FileSystemPath] = None,
    overrides: Any = None,
) -> ProjectConfig:
    """Load the project config at the specified location."""
    path = Path(filename) if filename else None

    try:
        path = resolve_packageable_path(path)
    except Exception as exc:
        raise InvalidProjectConfig(str(exc)) from None

    if path:
        if path.is_dir():
            if detected_path := locate_config(path):
                path = detected_path
            else:
                msg = f'Missing default config in the specified directory "{path}".'
                raise InvalidProjectConfig(msg)
    elif overrides is None:
        msg = "There are no config files available. Select a project or provide manual config overrides."
        raise InvalidProjectConfig(msg)

    with config_error_handler(path or "(overrides)"):
        if not path:
            config: Any = {}
        elif path.suffix == ".toml":
            config = toml.loads(path.read_text())
        elif path.suffix in [".yml", ".yaml"]:
            config = yaml.safe_load(path.read_text())
        else:
            config = json.loads(path.read_text())

        if not config:
            config = {}

        if path and path.name == "pyproject.toml":
            tool = config.get("tool")
            if tool is None or (config := tool.get("beet")) is None:
                raise InvalidProjectConfig(f"{path}: Missing [tool.beet] section")

            if poetry := tool.get("poetry"):
                if name := poetry.get("name"):
                    config.setdefault("name", name)
                if description := poetry.get("description"):
                    config.setdefault("description", description)
                if version := poetry.get("version"):
                    config.setdefault("version", version)
                if authors := poetry.get("authors"):
                    config.setdefault("author", authors[0])

        if overrides:
            config["overrides"] = [config.get("overrides"), overrides]

        config_dir = path.resolve().parent if path else None

        with local_import_path(str(config_dir)) if config_dir else nullcontext():
            return ProjectConfig(**config).resolve(config_dir or Path.cwd())


@contextmanager
def config_error_handler(path: FileSystemPath = "(unknown)"):
    """Handle configuration errors."""
    try:
        yield
    except (json.JSONDecodeError, toml.TomlDecodeError) as exc:
        raise InvalidProjectConfig(f"{path}:{exc.lineno}: {exc.msg}.") from exc  # type: ignore
    except yaml.MarkedYAMLError as exc:
        if exc.context_mark:
            exc.context_mark.name = str(path)
        if exc.problem_mark:
            exc.problem_mark.name = str(path)
        raise InvalidProjectConfig(str(exc)) from exc
    except FileNotFoundError as exc:
        raise InvalidProjectConfig(f"{path}: File not found.") from exc
    except ValidationError as exc:
        message = f"{path}: Validation error.\n\n"
        message += format_validation_error("config", exc)
        raise InvalidProjectConfig(message) from exc
