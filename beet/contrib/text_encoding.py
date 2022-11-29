"""Plugin that configures text encoding before writing out files."""


__all__ = [
    "TextEncodingOptions",
    "text_encoding",
]


from typing import Any, Optional

from beet import Context, ListOption, PluginOptions, TextFileBase, configurable


class TextEncodingOptions(PluginOptions):
    extensions: ListOption[str] = ListOption()
    encoding: str = "utf-8"
    errors: Optional[str] = None


def beet_default(ctx: Context):
    ctx.require(text_encoding)


@configurable(validator=TextEncodingOptions)
def text_encoding(ctx: Context, opts: TextEncodingOptions):
    """Plugin that configures text encoding before writing out files."""
    for pack in ctx.packs:
        for _, text_file in pack.list_files(
            *opts.extensions.entries(),
            extend=TextFileBase[Any],
        ):
            text_file.encoding = opts.encoding
            text_file.errors = opts.errors
