"""Plugin that builds a sandstone project."""


__all__ = [
    "SandstoneOption",
    "sandstone",
]


import subprocess
from typing import Optional

from pydantic import BaseModel

from beet import Context, configurable
from beet.core.utils import FileSystemPath


class SandstoneOption(BaseModel):
    path: Optional[FileSystemPath] = None


def beet_default(ctx: Context):
    ctx.require(sandstone)


@configurable(validator=SandstoneOption)
def sandstone(ctx: Context, opts: SandstoneOption):
    """Plugin that builds a given sandstone project."""
    directory = (ctx.directory / opts.path).resolve() if opts.path else ctx.directory
    output_directory = ctx.cache["sandstone"].directory

    arguments = ["npx", "sand", "build", "--path", str(output_directory)]
    subprocess.run(arguments, cwd=directory, check=True)

    ctx.data.load(next(output_directory.iterdir()))
