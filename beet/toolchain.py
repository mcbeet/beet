__all__ = ["Toolchain", "ErrorMessage"]


import os
import re
import json
from pathlib import Path
from itertools import chain
from textwrap import dedent
from typing import Sequence

from .common import FileSystemPath
from .project import Project
from .utils import ensure_optional_value


class ErrorMessage(Exception):
    pass


INIT_MODULE_TEMPLATE = """
    from beet import Context, Function


    def greeting(ctx: Context):
        message = ctx.meta["greeting"]
        ctx.data["{module_name}:greeting"] = Function(
            lines=[f"say {{message}}"],
            tags=["minecraft:load"],
        )
"""


class Toolchain:
    PROJECT_CONFIG_FILE = "beet.json"

    def __init__(self, directory: FileSystemPath = None):
        self.initial_directory = directory or os.getcwd()
        self._current_project = None

    def locate_project(self, initial_directory: FileSystemPath = None):
        start = Path(initial_directory or self.initial_directory).absolute()

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
        return ensure_optional_value(self._current_project)

    def build_project(self):
        ctx = self.current_project.build()

        for pack in [ctx.assets, ctx.data]:
            print(pack)

    def watch_project(self):
        yield

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

        if gitignore.is_file() and Project.CACHE_DIRECTORY not in (
            ignored := gitignore.read_text()
        ):
            ignored += f"\n# Beet cache\n{Project.CACHE_DIRECTORY}/\n"
            gitignore.write_text(ignored)
