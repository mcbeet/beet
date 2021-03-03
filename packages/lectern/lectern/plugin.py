__all__ = [
    "beet_default",
    "lectern",
]


from typing import Iterable, List, Optional, cast

from beet import Context
from beet.core.utils import JsonDict
from beet.toolchain.context import Plugin

from .document import Document


def beet_default(ctx: Context):
    config = ctx.meta.get("lectern", cast(JsonDict, {}))

    load = config.get("load", cast(List[str], []))
    snapshot = config.get("snapshot")
    external_files = config.get("external_files")

    ctx.require(lectern(load, snapshot, external_files))


def lectern(
    load: Iterable[str] = (),
    snapshot: Optional[str] = None,
    external_files: Optional[str] = None,
) -> Plugin:
    """Return a plugin that handles markdown files with lectern."""

    def plugin(ctx: Context):
        document = ctx.inject(Document)

        for pattern in load:
            for path in ctx.directory.glob(pattern):
                document.load(path)

        yield

        if snapshot:
            document.save(
                ctx.directory / snapshot,
                ctx.directory / external_files if external_files else None,
            )

    return plugin
