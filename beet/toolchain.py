__all__ = ["Toolchain", "ErrorMessage"]


import os
from pathlib import Path
from itertools import chain

from .common import FileSystemPath
from .project import Project
from .utils import ensure_optional_value


class ErrorMessage(ValueError):
    pass


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
        for pack in self.current_project.build():
            print(pack)

    def watch_project(self):
        yield

    def init_project(self):
        pass
