__all__ = [
    "beet_default",
    "lectern",
]


import subprocess
from glob import glob
from typing import Literal

from pydantic import BaseModel

from beet import Context, ListOption, PackageablePath, configurable

from .document import Document
from .loaders import LinkFragmentLoader


class LecternOptions(BaseModel):
    load: ListOption[PackageablePath] = ListOption()
    links: Literal["enable", "ignore", "disable"] = "enable"
    snapshot: str | None = None
    snapshot_sort: bool = False
    snapshot_flat: bool = False
    external_files: PackageablePath | None = None
    scripts: list[list[str]] = []


def beet_default(ctx: Context):
    ctx.require(lectern)


@configurable(validator=LecternOptions)
def lectern(ctx: Context, opts: LecternOptions):
    """Plugin that handles markdown files with lectern."""
    document = ctx.inject(Document)
    document.loaders.append(LinkFragmentLoader(status=opts.links))

    for pattern in opts.load.entries():
        for path in sorted(glob(str(ctx.directory / pattern))):
            document.load(path)

    for arguments in opts.scripts:
        result = subprocess.run(
            arguments,
            cwd=ctx.directory,
            check=True,
            stdout=subprocess.PIPE,
        )
        document.add_text(result.stdout.decode())

    yield

    if opts.snapshot:
        with (
            document.text_serializer.use_sorted_items(opts.snapshot_sort),
            document.markdown_serializer.use_sorted_items(opts.snapshot_sort),
            document.markdown_serializer.use_flat_format(opts.snapshot_flat),
        ):
            document.save(
                ctx.directory / opts.snapshot,
                ctx.directory / opts.external_files if opts.external_files else None,
            )
