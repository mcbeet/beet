__all__ = [
    "beet_default",
    "lectern",
]


import subprocess
from typing import List, Optional

from beet import Context, configurable
from pydantic import BaseModel

from .document import Document


class LecternOptions(BaseModel):
    load: List[str] = []
    snapshot: Optional[str] = None
    snapshot_flat: bool = False
    external_files: Optional[str] = None
    scripts: List[List[str]] = []


def beet_default(ctx: Context):
    ctx.require(lectern)


@configurable(validator=LecternOptions)
def lectern(ctx: Context, opts: LecternOptions):
    """Plugin that handles markdown files with lectern."""
    document = ctx.inject(Document)

    for pattern in opts.load:
        for path in ctx.directory.glob(pattern):
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
        with document.markdown_serializer.use_flat_format(opts.snapshot_flat):
            document.save(
                ctx.directory / opts.snapshot,
                ctx.directory / opts.external_files if opts.external_files else None,
            )
