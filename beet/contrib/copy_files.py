"""Plugin for copying files into the output resource pack and data pack."""


__all__ = [
    "CopyFilesOptions",
    "copy_files",
    "resolve_file_mapping",
    "guess_file_type",
]


import mimetypes
import os
from glob import glob
from pathlib import Path
from typing import Dict, Iterator, Tuple, Type

from beet import (
    BinaryFile,
    Context,
    JsonFile,
    ListOption,
    PackageablePath,
    PackFile,
    PluginOptions,
    PngFile,
    TextFile,
    YamlFile,
    configurable,
)
from beet.core.utils import FileSystemPath


class CopyFilesOptions(PluginOptions):
    resource_pack: Dict[str, ListOption[PackageablePath]] = {}
    data_pack: Dict[str, ListOption[PackageablePath]] = {}
    output: Dict[str, ListOption[PackageablePath]] = {}


def beet_default(ctx: Context):
    ctx.require(copy_files)


@configurable(validator=CopyFilesOptions)
def copy_files(ctx: Context, opts: CopyFilesOptions):
    """Plugin for copying files."""
    for pack, files in [
        (ctx.assets, resolve_file_mapping(opts.resource_pack, ctx.directory)),
        (ctx.data, resolve_file_mapping(opts.data_pack, ctx.directory)),
    ]:
        for dst, src, file_type in files:
            pack.extra[dst] = file_type(source_path=src)

    if ctx.output_directory:
        for dst, src, file_type in resolve_file_mapping(opts.output, ctx.directory):
            target_directory = ctx.output_directory / dst
            target_directory.parent.mkdir(parents=True, exist_ok=True)
            file_type(source_path=src).dump(ctx.output_directory, dst)


def resolve_file_mapping(
    mapping: Dict[str, ListOption[PackageablePath]],
    directory: Path,
) -> Iterator[Tuple[str, Path, Type[PackFile]]]:
    """Expand glob patterns and guess the type of each file."""
    for key, value in mapping.items():
        entries = [
            Path(entry)
            for pattern in value.entries()
            for entry in glob(str(directory / pattern))
        ]
        for entry in entries:
            dst = f"{key}/{entry.name}" if len(entries) > 1 else key
            if entry.is_dir():
                for root, _, files in os.walk(entry):
                    for filename in files:
                        path = Path(root, filename)
                        file_dst = f"{dst}/{path.relative_to(entry).as_posix()}"
                        yield file_dst, path, guess_file_type(path)
            else:
                yield dst, entry, guess_file_type(entry)


def guess_file_type(filename: FileSystemPath) -> Type[PackFile]:
    """Helper to figure out the most appropriate file type depending on a filename."""
    filename = str(filename)

    if filename.endswith(".json"):
        return JsonFile
    elif filename.endswith((".yml", ".yaml")):
        return YamlFile
    elif filename.endswith(".png"):
        return PngFile

    mime_type, _ = mimetypes.guess_type(filename, strict=False)
    if mime_type and mime_type.startswith("text/"):
        return TextFile

    return BinaryFile
