"""Plugin for copying files into the output resource pack and data pack."""


__all__ = [
    "CopyFilesOptions",
    "copy_files",
    "resolve_file_mapping",
    "guess_file_type",
]


import mimetypes
from pathlib import Path
from typing import Dict, List, Tuple, Type, Union

from pydantic import BaseModel

from beet import (
    BinaryFile,
    Context,
    JsonFile,
    PackFile,
    PngFile,
    TextFile,
    YamlFile,
    configurable,
)
from beet.core.utils import FileSystemPath


class CopyFilesOptions(BaseModel):
    resource_pack: Dict[str, Union[str, List[str]]] = {}
    data_pack: Dict[str, Union[str, List[str]]] = {}
    output: Dict[str, Union[str, List[str]]] = {}


def beet_default(ctx: Context):
    ctx.require(copy_files)


@configurable(validator=CopyFilesOptions)
def copy_files(ctx: Context, opts: CopyFilesOptions):
    """Plugin for copying files."""
    for pack, files in [
        (ctx.assets, resolve_file_mapping(opts.resource_pack, ctx.directory)),
        (ctx.data, resolve_file_mapping(opts.data_pack, ctx.directory)),
    ]:
        for dst, src in files.items():
            if len(src) == 1:
                path, file_type = src[0]
                pack.extra[dst] = file_type(source_path=path)
            else:
                for path, file_type in src:
                    pack.extra[f"{dst}/{path.name}"] = file_type(source_path=path)

    if ctx.output_directory:
        for dst, src in resolve_file_mapping(opts.output, ctx.directory).items():
            if len(src) == 1:
                path, file_type = src[0]
                file_type(source_path=path).dump(ctx.output_directory, dst)
            else:
                target_directory = ctx.output_directory / dst
                target_directory.mkdir(parents=True, exist_ok=True)
                for path, file_type in src:
                    file_type(source_path=path).dump(target_directory, path.name)


def resolve_file_mapping(
    mapping: Dict[str, Union[str, List[str]]],
    directory: Path,
) -> Dict[str, List[Tuple[Path, Type[PackFile]]]]:
    """Expand glob patterns and guess the type of each file."""
    return {
        key: [
            (filename, guess_file_type(filename))
            for pattern in ([value] if isinstance(value, str) else value)
            for filename in directory.glob(pattern)
        ]
        for key, value in mapping.items()
    }


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
