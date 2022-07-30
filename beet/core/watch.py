__all__ = [
    "DirectoryWatcher",
    "FileChanges",
    "detect_repeated_changes",
]


import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, Iterator, Literal, Optional, Sequence, Tuple, cast

from pathspec import PathSpec

from .utils import FileSystemPath, extra_field

FileChanges = Dict[str, Literal["created", "edited", "removed"]]


@dataclass
class DirectoryWatcher:
    """Iterator that detects and yields file changes by polling the filesystem."""

    path: FileSystemPath
    interval: float = 0.6
    ignore: PathSpec = field(init=False)

    ignore_file: Optional[FileSystemPath] = extra_field(default=None)
    ignore_patterns: Sequence[str] = extra_field(default=())

    files: Dict[str, float] = extra_field(init=False, default_factory=dict)

    def __post_init__(self):
        self.ignore_patterns = list(self.ignore_patterns)

        if self.ignore_file:
            ignore_file = Path(self.ignore_file)

            if ignore_file.parts == (ignore_file.name,):
                for directory in Path(self.path, ignore_file).parents:
                    if (path := (directory / ignore_file)).is_file():
                        ignore_file = path
                        break

            if ignore_file.is_file():
                self.ignore_patterns += [
                    pattern
                    for line in ignore_file.read_text().splitlines()
                    if not line.startswith("#") and (pattern := line.strip())
                ]

        self.ignore = PathSpec.from_lines("gitwildmatch", self.ignore_patterns)

    def __iter__(self) -> Iterator[FileChanges]:
        while True:
            if changes := self.poll():
                yield changes
            time.sleep(self.interval)

    def poll(self) -> FileChanges:
        """Return the files created, edited, or removed since the last poll."""
        changes: FileChanges = {}
        new_files = dict(self.walk())

        for filename, mtime in new_files.items():
            if (previous := self.files.get(filename)) == mtime:
                continue
            changes[filename] = "edited" if previous else "created"

        removed = self.files.keys() - new_files.keys()
        changes.update(
            cast(
                Dict[str, Literal["removed"]],
                {filename: "removed" for filename in removed},
            )
        )

        self.files = new_files
        return changes

    def walk(
        self,
        path: Optional[FileSystemPath] = None,
    ) -> Iterator[Tuple[str, float]]:
        """Walk down the watched directories."""
        base_path = Path(self.path).resolve()
        directory = base_path / path if path else base_path

        for entry in os.scandir(directory):
            entry_path = Path(entry.path)
            relative_path = entry_path.relative_to(base_path)

            if self.ignore.match_file(relative_path):
                continue

            if entry_path.is_dir():
                yield from self.walk(relative_path)
            else:
                yield str(relative_path), entry.stat().st_mtime


def detect_repeated_changes(
    source: Iterable[FileChanges],
    min_interval: float = 1.2,
    max_streak: int = 3,
) -> Iterator[Tuple[bool, FileChanges]]:
    """Detect repeated changes."""
    streak: int = 0
    last_build: float = 0.0
    last_changes: FileChanges = {}

    for changes in source:
        if time.time() - last_build < min_interval and changes == last_changes:
            streak += 1
        else:
            streak = 0

        yield streak > max_streak, changes

        last_build = time.time()
        last_changes = changes
