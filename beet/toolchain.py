__all__ = ["Toolchain", "ErrorMessage", "locate_minecraft"]


import os
import re
import json
import platform
from pathlib import Path
from itertools import chain
from textwrap import dedent
from typing import Sequence, Optional, Dict, Tuple, Iterator

from .common import FileSystemPath, Pack
from .project import Project
from .watch import DirectoryWatcher, FileChanges


class ErrorMessage(Exception):
    pass


INIT_MODULE_TEMPLATE = """
    from beet import Context, Function


    def greeting(ctx: Context):
        message = ctx.meta["greeting"]
        ctx.data["{module_name}:greeting"] = Function(
            [f"say {{message}}"],
            tags=["minecraft:load"],
        )
"""


class Toolchain:
    PROJECT_CONFIG_FILE = "beet.json"

    initial_directory: FileSystemPath
    _current_project: Optional[Project]

    def __init__(self, directory: FileSystemPath = None):
        self.initial_directory = directory or os.getcwd()
        self._current_project = None

    def locate_project(self, initial_directory: FileSystemPath = None):
        start = Path(initial_directory or self.initial_directory).resolve()

        for directory in chain([start], start.parents):
            config = directory / self.PROJECT_CONFIG_FILE

            if config.is_file():
                self._current_project = Project.from_config(config)
                return

        raise ErrorMessage(f"Couldn't find any project configuration file in {start}.")

    @property
    def current_project(self) -> Project:
        if not self._current_project:
            self.locate_project()
        assert self._current_project
        return self._current_project

    def build_project(self):
        ctx = self.current_project.build()
        output: Dict[str, Pack] = {"assets_dir": ctx.assets, "data_dir": ctx.data}

        for link_key, pack in output.items():
            if not pack:
                continue

            pack.dump(ctx.output_directory, overwrite=True)

            if link_dir := ctx.cache["link"].json.get(link_key):
                pack.dump(link_dir, overwrite=True)

    def watch_project(self) -> Iterator[FileChanges]:
        for changes in DirectoryWatcher(
            self.current_project.directory,
            ignore_file=".gitignore",
            ignore_patterns=[
                f"/{self.current_project.output_directory}",
                f"/{self.current_project.cache_directory}",
                "*.tmp",
            ],
        ):
            self._current_project = None
            yield changes

    def clear_cache(self, selected_caches: Sequence[str] = ()):
        with self.current_project.context() as ctx:
            if selected_caches:
                for cache_name in selected_caches:
                    del ctx.cache[cache_name]
            else:
                ctx.cache.clear()

    def inspect_cache(self, selected_caches: Sequence[str] = ()) -> str:
        with self.current_project.context() as ctx:
            if not selected_caches:
                ctx.cache.preload()
                selected_caches = tuple(sorted(ctx.cache.keys()))

            return (
                "\n".join(f"{ctx.cache[name]}\n" for name in selected_caches)
                or "The cache is completely clear.\n"
            )

    def clear_project_link(self):
        with self.current_project.context() as ctx:
            del ctx.cache["link"]

    def link_project(
        self, directory: FileSystemPath = None
    ) -> Tuple[Optional[Path], Optional[Path]]:
        minecraft = locate_minecraft()
        target_path = Path(directory).resolve() if directory else minecraft

        if not target_path:
            raise ErrorMessage("Couldn't locate the Minecraft folder.")

        assets_dir: Optional[Path] = None
        data_dir: Optional[Path] = None

        if (
            not target_path.is_dir()
            and directory
            and Path(directory).parts == (directory,)
            and not (
                minecraft and (target_path := minecraft / "saves" / directory).is_dir()
            )
        ):
            raise ErrorMessage(
                f"Couldn't find {str(directory)!r} in the Minecraft save folder."
            )

        if (target_path / "level.dat").is_file():
            data_dir = target_path / "datapacks"
            target_path = target_path.parent.parent
        if (resource_packs := target_path / "resourcepacks").is_dir():
            assets_dir = resource_packs

        if not (assets_dir or data_dir):
            raise ErrorMessage(
                "Couldn't establish any link through the specified directory."
            )

        with self.current_project.context() as ctx:
            ctx.cache["link"].json.update(
                assets_dir=str(assets_dir), data_dir=str(data_dir)
            )

        return assets_dir, data_dir

    def init_project(
        self,
        name: str,
        description: str = None,
        author: str = None,
        version: str = None,
    ):
        config = Path(self.initial_directory, self.PROJECT_CONFIG_FILE)

        if config.exists():
            raise ErrorMessage("Configuration file already exists.")

        module_name = re.sub(r"[^a-z0-9]+", "_", name.lower())

        arguments = {
            "name": name,
            "description": description,
            "author": author,
            "version": version,
        }

        json_config = {
            **{key: value for key, value in arguments.items() if value is not None},
            "generators": [f"{module_name}.greeting"],
            "meta": {"greeting": "Hello, world!"},
        }

        config.write_text(json.dumps(json_config, indent=2))

        module_file = Path(self.initial_directory, f"{module_name}.py")

        if not module_file.exists():
            content = INIT_MODULE_TEMPLATE.format(module_name=module_name)
            module_file.write_text(dedent(content).strip() + "\n")

        gitignore = Path(self.initial_directory, ".gitignore")

        if gitignore.is_file() and Project.cache_directory not in (
            ignored := gitignore.read_text()
        ):
            ignored += f"\n# Beet cache\n{Project.cache_directory}/\n"
            gitignore.write_text(ignored)


def locate_minecraft() -> Optional[Path]:
    path = None
    system = platform.system()

    if system == "Linux":
        path = Path("~/.minecraft").expanduser()
    elif system == "Darwin":
        path = Path("~/Library/Application Support/minecraft").expanduser()
    elif system == "Windows":
        path = Path(os.path.expandvars(r"%APPDATA%\.minecraft"))

    return path.resolve() if path and path.is_dir() else None
