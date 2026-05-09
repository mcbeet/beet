"""Plugin that outputs the data pack and the resource pack in a local directory."""

__all__ = [
    "OutputOptions",
    "output",
]


import filecmp
import os
from pathlib import Path

from beet import Context, ListOption, PluginOptions, configurable
from beet.core.utils import FileSystemPath, log_time_scope
from beet.library.base import Pack, PackFile
from beet.library.utils import list_files as list_dir_files


class OutputOptions(PluginOptions):
    directory: ListOption[FileSystemPath] | None = None
    incremental: bool | None = None


def beet_default(ctx: Context):
    ctx.require(output)


def incremental_save(pack: Pack, output_path: Path) -> None:
    """ Save a pack incrementally: delete removed files, write new/changed files, skip unchanged. """
    # Build expected set: posix-style relative paths -> PackFile
    expected: dict[str, PackFile] = dict(pack.list_files())

    # Build disk set: posix-style relative paths currently on disk
    disk_set: set[str] = set()
    if output_path.is_dir():
        for rel in list_dir_files(output_path):
            disk_set.add(rel.as_posix())

    # Delete files that are no longer present in the pack
    deleted_files: set[str] = disk_set - expected.keys()
    for rel_path in deleted_files:
        disk_path: Path = output_path / rel_path
        disk_path.unlink(missing_ok=True)

    # Remove empty directories left after deletions (bottom-up)
    for dirpath, _dirnames, _filenames in os.walk(output_path, topdown=False):
        dir_obj = Path(dirpath)
        if dir_obj == output_path:
            continue
        try:
            dir_obj.rmdir()  # only succeeds if empty
        except OSError:
            pass  # not empty - leave it

    # Ensure the root output directory exists
    if output_path.exists() and not output_path.is_dir():
        output_path.unlink()
    output_path.mkdir(parents=True, exist_ok=True)

    # For each expected file, compare with disk and write if new/changed
    for rel_path, pack_file in expected.items():
        disk_path: Path = output_path / rel_path

        # New file, write directly without comparison
        if not disk_path.exists():
            disk_path.parent.mkdir(parents=True, exist_ok=True)
            pack_file.dump(output_path, rel_path)

        # Existing file: compare before writing
        else:
            changed: bool = True
            try:
                # Fast path: if the pack file still points directly to a source path, avoid loading content into memory
                if (
                    pack_file.source_path is not None
                    and pack_file.source_start is None
                    and pack_file.source_stop is None
                ):
                    changed = not filecmp.cmp(pack_file.source_path, disk_path, shallow=False)
                else:
                    # Standard path: use beet's own content equality
                    existing_file: PackFile = type(pack_file)(source_path=disk_path)
                    changed = not pack_file.content_equal(existing_file)
            except Exception:
                changed = True  # Fallback to overwrite on any error

            if changed:
                pack_file.dump(output_path, rel_path)


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
            for pack in packs:
                for path in paths:
                    if incremental and not pack.zipped and pack.name is not None:
                        incremental_save(pack, Path(path) / pack.name)
                    else:
                        pack.save(path, overwrite=True)

