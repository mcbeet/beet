"""Plugin that builds a sandstone project."""


__all__ = [
    "sandstone",
]


import subprocess
from typing import Optional, cast

from beet import Context, Plugin
from beet.core.utils import FileSystemPath, JsonDict


def beet_default(ctx: Context):
    config = ctx.meta.get("sandstone", cast(JsonDict, {}))

    path = config.get("path")

    ctx.require(sandstone(path))


def sandstone(path: Optional[FileSystemPath] = None) -> Plugin:
    """Return a plugin that builds a given sandstone project."""

    def plugin(ctx: Context):
        directory = (ctx.directory / path).resolve() if path else ctx.directory
        output_directory = ctx.cache["sandstone"].directory

        arguments = ["npx", "sand", "build", "--path", str(output_directory)]
        subprocess.run(arguments, cwd=directory, check=True)

        ctx.data.load(next(output_directory.iterdir()))

    return plugin
