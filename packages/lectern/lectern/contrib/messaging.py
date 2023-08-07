"""Plugin for handling markdown coming from messaging apps."""


__all__ = [
    "MessagingOptions",
    "messaging",
]


from typing import Literal, Optional

from beet import Context, ErrorMessage, Function, ListOption, configurable
from pydantic import BaseModel

from lectern import Document, LinkFragmentLoader


class MessagingOptions(BaseModel):
    links: Literal["enable", "ignore", "disable"] = "enable"
    input: ListOption[str] = ListOption()
    nothing_error: Optional[str] = None


def beet_default(ctx: Context):
    ctx.require(messaging)


@configurable(validator=MessagingOptions)
def messaging(ctx: Context, opts: MessagingOptions):
    """Plugin for handling markdown coming from messaging apps.

    The extractor cache is disabled to prevent remote files from being
    written to disk. If the message doesn't contain any fragment we try to
    form a default function by concatenating all code blocks.
    """
    document = ctx.inject(Document)
    document.loaders.append(LinkFragmentLoader(status=opts.links))
    document.markdown_extractor.cache = None

    directives = document.directives.resolve()

    for message in opts.input.entries():
        if fragments := list(
            document.markdown_extractor.parse_fragments(message, directives)
        ):
            document.markdown_extractor.apply_directives(
                ctx.assets, ctx.data, directives, fragments, document.loaders
            )
        elif code_blocks := [
            token.content
            for token in document.markdown_extractor.parser.parse(message)  # type: ignore
            if token.type in ["fence", "code_block"]
        ]:
            ctx.generate("default", Function("\n".join(code_blocks)))
        elif opts.nothing_error:
            raise ErrorMessage(opts.nothing_error)
