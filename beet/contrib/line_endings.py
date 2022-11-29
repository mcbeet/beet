"""Plugin that configures line endings before writing out files."""


__all__ = [
    "LineEndingsOptions",
    "line_endings",
]


from typing import Any, Optional

from beet import Context, ListOption, PluginOptions, TextFileBase, configurable


class LineEndingsOptions(PluginOptions):
    extensions: ListOption[str] = ListOption()
    newline: Optional[str] = None


def beet_default(ctx: Context):
    ctx.require(line_endings)


@configurable(validator=LineEndingsOptions)
def line_endings(ctx: Context, opts: LineEndingsOptions):
    """Plugin that configures line endings before writing out files."""
    for pack in ctx.packs:
        for _, text_file in pack.list_files(
            *opts.extensions.entries(),
            extend=TextFileBase[Any],
        ):
            text_file.newline = opts.newline
