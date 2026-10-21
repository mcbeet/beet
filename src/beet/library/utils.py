__all__ = [
    "list_extensions",
    "list_files",
    "list_origin",
    "list_origin_folders",
]


import os
from collections.abc import Iterator, Mapping
from itertools import accumulate
from pathlib import Path, PurePath, PurePosixPath
from zipfile import ZipFile

from beet.core.file import FileOrigin
from beet.core.utils import FileSystemPath


def list_files(directory: FileSystemPath) -> Iterator[Path]:
    for root, _, files in os.walk(directory):
        for filename in files:
            yield Path(root, filename).relative_to(directory)


def list_origin(origin: FileOrigin) -> list[PurePath]:
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


def list_origin_folders(prefix: str, origin: FileOrigin) -> dict[str, list[PurePath]]:
    preparts = tuple(filter(None, prefix.split("/")))

    folders: dict[str, list[PurePath]] = {}

    current_name = ""
    current_folder: list[PurePath] = []

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


def modified_suffixes(path: PurePath) -> list[str]:
    """
    Equivalent to path.suffixes but support file with empty name
    """
    name = path.name
    if name.endswith("."):
        return []
    if name.startswith("."):
        name = name[1:]
        return ["." + suffix for suffix in name.split(".")]
    return path.suffixes


def list_extensions(path: PurePath) -> list[str]:
    extensions: list[str] = list(
        accumulate(reversed(modified_suffixes(path)), lambda a, b: b + a)
    )
    extensions.reverse()
    extensions.append("")
    return extensions
