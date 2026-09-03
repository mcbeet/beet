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
    # Slicing the prefix off the string os.walk already built is several times faster
    # than rebuilding a Path per file just to have relative_to take it apart again
    base: str = os.fspath(directory)
    prefix_length: int = len(base) + (0 if base.endswith(("/", os.sep)) else 1)
    for root, _, files in os.walk(base):
        relative_root = root[prefix_length:]
        for filename in files:
            yield Path(relative_root, filename)


def list_origin(origin: FileOrigin) -> List[PurePath]:
    if isinstance(origin, ZipFile):
        filenames = (
            PurePosixPath(file_info.filename)
            for file_info in origin.infolist()
            if not file_info.is_dir()
        )
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
                if name == "__MACOSX":
                    continue
                current_name = name
                current_folder = folders.setdefault(name, [])

            current_folder.append(filename)

    return folders


def list_extensions(path: PurePath) -> List[str]:
    extensions: List[str] = list(
        accumulate(reversed(path.suffixes), lambda a, b: b + a)
    )
    extensions.reverse()
    extensions.append("")
    return extensions
