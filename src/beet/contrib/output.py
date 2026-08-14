"""Plugin that outputs the data pack and the resource pack in a local directory."""

__all__ = [
    "OutputOptions",
    "output",
]


import filecmp
import hashlib
import json
import os
from pathlib import Path

from beet import Context, ListOption, PluginOptions, configurable
from beet.core.utils import FileSystemPath, log_time_scope
from beet.library.base import Pack, PackFile

ManifestEntry = tuple[int, int, str]
""" Size, modification time in nanoseconds and content signature of a file this plugin wrote. """


class OutputOptions(PluginOptions):
    directory: ListOption[FileSystemPath] | None = None
    incremental: bool | None = None


def beet_default(ctx: Context):
    ctx.require(output)


def scan_directory(directory: Path) -> dict[str, tuple[int, int]]:
    """ Return the size and modification time of every file below the directory, efficiently.
    One `scandir` pass answers both "which files are there" and "have they changed". """
    result: dict[str, tuple[int, int]] = {}

    def walk(path: str, prefix: str) -> None:
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_dir(follow_symlinks=False):
                    walk(entry.path, f"{prefix}{entry.name}/")
                else:
                    stat = entry.stat()
                    result[f"{prefix}{entry.name}"] = (stat.st_size, stat.st_mtime_ns)

    if directory.is_dir():
        walk(str(directory), "")
    return result


def prune_empty_directories(directory: Path) -> None:
    """ Remove every directory left empty below the given root, deepest first. """
    for dirpath, _dirnames, _filenames in os.walk(directory, topdown=False):
        if dirpath != str(directory):
            try:
                os.rmdir(dirpath)
            except OSError:
                pass  # Not empty, leave it alone


def content_signature(pack_file: PackFile) -> str:
    """ Return a signature that changes whenever the bytes the pack file would write change.

    A file still backed by an untouched source is signed from that source's stat, so unchanged assets
    never have to be loaded into memory at all.

    Args:
        pack_file (PackFile): The file to sign.
    Returns:
        str: Either `source:<size>:<mtime>` or `sha1:<digest>`.
    """
    if (
        pack_file.source_path is not None
        and pack_file.source_start is None
        and pack_file.source_stop is None
    ):
        stat = os.stat(pack_file.source_path)
        return f"source:{stat.st_size}:{stat.st_mtime_ns}"

    serialized: str | bytes = pack_file.ensure_serialized()
    if isinstance(serialized, str):
        serialized = serialized.encode(getattr(pack_file, "encoding", None) or "utf-8")
    return f"sha1:{hashlib.sha1(serialized).hexdigest()}"


def file_differs(pack_file: PackFile, disk_path: Path) -> bool:
    """ Return whether the file on disk differs from what the pack file would write, by reading both. """
    try:
        if (
            pack_file.source_path is not None
            and pack_file.source_start is None
            and pack_file.source_stop is None
        ):
            return not filecmp.cmp(pack_file.source_path, disk_path, shallow=False)

        serialized: str | bytes = pack_file.ensure_serialized()
        if isinstance(serialized, str):
            encoding: str = getattr(pack_file, "encoding", None) or "utf-8"
            return disk_path.read_text(encoding=encoding) != serialized
        return disk_path.read_bytes() != serialized
    except Exception:
        return True


def load_manifest(manifest_path: Path | None) -> dict[str, ManifestEntry]:
    """ Read the record of what the previous build wrote, treating any problem as an empty record. """
    if manifest_path is None:
        return {}
    try:
        raw = json.loads(manifest_path.read_text("utf-8"))
        return {
            key: (int(value[0]), int(value[1]), str(value[2]))
            for key, value in raw.items()
            if len(value) == 3
        }
    except (OSError, ValueError, TypeError, KeyError, IndexError):
        return {}


def incremental_save(
    pack: Pack, output_path: Path, manifest_path: Path | None = None
) -> None:
    """ Save a pack incrementally: delete removed files, write new/changed files, skip unchanged.

    Args:
        pack (Pack): The pack to write out.
        output_path (Path): The directory the pack is written to.
        manifest_path (Path | None): Where to keep the record, or None to compare against the disk every time.
    """
    expected: dict[str, PackFile] = dict(pack.list_files())
    manifest: dict[str, ManifestEntry] = load_manifest(manifest_path)
    on_disk: dict[str, tuple[int, int]] = scan_directory(output_path)

    # Delete files that are no longer part of the pack, and the directories that leaves empty
    deleted_files: set[str] = on_disk.keys() - expected.keys()
    for rel_path in deleted_files:
        (output_path / rel_path).unlink(missing_ok=True)
    if deleted_files:
        prune_empty_directories(output_path)

    # Ensure the root output directory exists
    if output_path.exists() and not output_path.is_dir():
        output_path.unlink()
    output_path.mkdir(parents=True, exist_ok=True)

    written: dict[str, ManifestEntry] = {}
    for rel_path, pack_file in expected.items():
        signature: str = content_signature(pack_file)
        recorded: ManifestEntry | None = manifest.get(rel_path)
        current: tuple[int, int] | None = on_disk.get(rel_path)

        # Untouched since we wrote it and still holding the same content, nothing to do
        if recorded is not None and current == recorded[:2] and recorded[2] == signature:
            written[rel_path] = recorded
            continue

        disk_path: Path = output_path / rel_path

        # No record to trust but the file is there, so fall back to comparing the bytes
        if recorded is None and current is not None and not file_differs(pack_file, disk_path):
            written[rel_path] = (*current, signature)
            continue

        disk_path.parent.mkdir(parents=True, exist_ok=True)
        pack_file.dump(output_path, rel_path)
        stat = disk_path.stat()
        written[rel_path] = (stat.st_size, stat.st_mtime_ns, signature)

    if manifest_path is not None:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(written), "utf-8")


@configurable(validator=OutputOptions)
def output(ctx: Context, opts: OutputOptions):
    """ Plugin that outputs the data pack and the resource pack in a local directory. """
    if opts.directory is None:
        return

    # Check both opts and ctx.meta.output for incremental flag
    incremental: bool | None = opts.incremental
    if incremental is None:
        meta_opts = ctx.meta.get("output")
        if isinstance(meta_opts, dict):
            incremental = bool(meta_opts.get("incremental", False))

    paths: list[Path] = [ctx.directory / path for path in opts.directory.entries()]
    packs: list[Pack] = list(filter(None, ctx.packs))

    if paths and packs:
        with log_time_scope("Output files."):
            cache = ctx.cache["output_incremental"]
            for pack in packs:
                for path in paths:
                    if incremental and not pack.zipped and pack.name is not None:
                        target: Path = Path(path) / pack.name
                        incremental_save(pack, target, cache.get_path(f"manifest:{target}"))
                    else:
                        pack.save(path, overwrite=True)

