__all__ = [
    "list_files",
    "list_origin",
    "list_origin_folders",
    "list_extensions",
]


import os
from itertools import accumulate
from pathlib import Path, PurePath, PurePosixPath
from typing import Dict, Iterator, List, Mapping
from zipfile import ZipFile

from beet.core.file import FileOrigin
from beet.core.utils import FileSystemPath


def list_files(directory: FileSystemPath) -> Iterator[Path]:
    for root, _, files in os.walk(directory):
        for filename in files:
            yield Path(root, filename).relative_to(directory)


def list_origin(origin: FileOrigin) -> List[PurePath]:
    if isinstance(origin, ZipFile):
        filenames = map(PurePosixPath, origin.namelist())
    elif isinstance(origin, Mapping):
        filenames = map(PurePosixPath, origin)
    elif Path(origin).is_file():
        filenames = [PurePosixPath()]
    else:
        filenames = list_files(origin)
    return sorted(filenames)


def list_origin_folders(prefix: str, origin: FileOrigin) -> Dict[str, List[PurePath]]:
    preparts = tuple(filter(None, prefix.split("/")))

    folders: Dict[str, List[PurePath]] = {}

    current_name = ""
    current_folder: List[PurePath] = []

    for filename in list_origin(origin):
        parts = preparts + filename.parts

        if len(parts) > 1:
            name = parts[0]

            if name != current_name:
                current_name = name
                current_folder = folders.setdefault(name, [])

            current_folder.append(filename)

    return folders


def list_extensions(path: PurePath) -> List[str]:
    extensions: List[str] = list(
        accumulate(reversed(path.suffixes), lambda a, b: b + a)  # type: ignore
    )
    extensions.reverse()
    extensions.append("")
    return extensions
