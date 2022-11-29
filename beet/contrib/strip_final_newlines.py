"""Plugin that strips final newlines in text files."""


__all__ = [
    "StripFinalNewlinesSerializer",
    "StripFinalNewlinesOptions",
    "strip_final_newlines",
]


from dataclasses import dataclass
from typing import Any, Callable

from beet import Context, ListOption, PluginOptions, TextFileBase, configurable


class StripFinalNewlinesOptions(PluginOptions):
    extensions: ListOption[str] = ListOption()


def beet_default(ctx: Context):
    ctx.require(strip_final_newlines)


@dataclass
class StripFinalNewlinesSerializer:
    """Wrap existing serializer and strip final newline."""

    serializer: Callable[[Any], str]

    def __call__(self, content: Any) -> str:
        raw = self.serializer(content)
        if raw.endswith("\n"):
            raw = raw[:-1]
        return raw


@configurable(validator=StripFinalNewlinesOptions)
def strip_final_newlines(ctx: Context, opts: StripFinalNewlinesOptions):
    """Plugin that strips final newlines in text files."""
    for pack in ctx.packs:
        for _, text_file in pack.list_files(
            *opts.extensions.entries(),
            extend=TextFileBase[Any],
        ):
            text_file.serializer = StripFinalNewlinesSerializer(text_file.serializer)
            if isinstance(raw := text_file.get_content(), str) and raw.endswith("\n"):
                text_file.text = raw[:-1]
