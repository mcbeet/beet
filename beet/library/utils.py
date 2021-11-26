__all__ = [
    "list_files",
    "list_extensions",
]


import os
from itertools import accumulate
from pathlib import Path, PurePath
from typing import Iterator, List

from beet.core.utils import FileSystemPath


def list_files(directory: FileSystemPath) -> Iterator[Path]:
    for root, _, files in os.walk(directory):
        for filename in files:
            yield Path(root, filename).relative_to(directory)


def list_extensions(path: PurePath) -> List[str]:
    extensions: List[str] = list(
        accumulate(reversed(path.suffixes), lambda a, b: b + a)  # type: ignore
    )
    extensions.reverse()
    return extensions
