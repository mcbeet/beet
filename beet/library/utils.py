__all__ = [
    "list_files",
]


import os
from pathlib import Path
from typing import Iterator

from beet.core.utils import FileSystemPath


def list_files(directory: FileSystemPath) -> Iterator[Path]:
    for root, _, files in os.walk(directory):
        for filename in files:
            yield Path(root, filename).relative_to(directory)
