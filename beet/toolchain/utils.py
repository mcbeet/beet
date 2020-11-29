__all__ = [
    "format_directory",
]


from pathlib import Path
from typing import Iterator

from beet.shared_utils import FileSystemPath


def format_directory(directory: FileSystemPath, prefix: str = "") -> Iterator[str]:
    entries = list(sorted(Path(directory).iterdir()))
    indents = ["├─"] * (len(entries) - 1) + ["└─"]

    for indent, entry in zip(indents, entries):
        yield f"{prefix}{indent} {entry.name}"

        if entry.is_dir():
            indent = "│  " if indent == "├─" else "   "
            yield from format_directory(entry, prefix + indent)
