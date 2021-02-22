__all__ = [
    "beet_default",
    "lectern",
]


from typing import Iterable, Optional

from beet import Context
from beet.toolchain.context import Plugin

from .document import Document


def beet_default(ctx: Context):
    config = ctx.meta.get("lectern", {})

    load = config.get("load", [])
    output = config.get("output")
    output_files = config.get("output_files")

    ctx.require(lectern(load, output, output_files))


def lectern(
    load: Iterable[str] = (),
    output: Optional[str] = None,
    output_files: Optional[str] = None,
) -> Plugin:
    """Return a plugin that handles markdown files with lectern."""

    def plugin(ctx: Context):
        document = ctx.inject(Document)

        for pattern in load:
            for path in ctx.directory.glob(pattern):
                document.load(path)

        yield

        if output:
            document.save(
                ctx.directory / output,
                ctx.directory / output_files if output_files else None,
            )

    return plugin
