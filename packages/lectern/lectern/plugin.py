__all__ = [
    "beet_default",
    "lectern",
]


import subprocess
from typing import Iterable, List, Optional, cast

from beet import Context, Plugin
from beet.core.utils import JsonDict

from .document import Document


def beet_default(ctx: Context):
    config = ctx.meta.get("lectern", cast(JsonDict, {}))

    load = config.get("load", ())
    snapshot = config.get("snapshot")
    external_files = config.get("external_files")
    scripts = config.get("scripts", ())

    ctx.require(lectern(load, snapshot, external_files, scripts))


def lectern(
    load: Iterable[str] = (),
    snapshot: Optional[str] = None,
    external_files: Optional[str] = None,
    scripts: Iterable[List[str]] = (),
) -> Plugin:
    """Return a plugin that handles markdown files with lectern."""

    def plugin(ctx: Context):
        document = ctx.inject(Document)

        for pattern in load:
            for path in ctx.directory.glob(pattern):
                document.load(path)

        for arguments in scripts:
            result = subprocess.run(
                arguments,
                cwd=ctx.directory,
                check=True,
                stdout=subprocess.PIPE,
            )
            document.add_text(result.stdout.decode())

        yield

        if snapshot:
            document.save(
                ctx.directory / snapshot,
                ctx.directory / external_files if external_files else None,
            )

    return plugin
