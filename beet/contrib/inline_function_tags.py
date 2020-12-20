__all__ = [
    "InlineFunctionTags",
]


from typing import Any

from jinja2.ext import Extension
from jinja2.nodes import ContextReference, ExprStmt, Node

from beet import Context, FunctionTag, RenderInfo


def beet_default(ctx: Context):
    ctx.template.env.add_extension(InlineFunctionTags)  # type: ignore


class InlineFunctionTags(Extension):
    """A Jinja extension that allows you to declare function tags inline."""

    tags = {"tag"}

    def parse(self, parser: Any) -> Node:
        lineno = next(parser.stream).lineno
        args = [parser.parse_expression(), ContextReference()]
        handler = self.call_method("_function_tag_handler", args, lineno=lineno)  # type: ignore
        return ExprStmt(handler, lineno=lineno)  # type: ignore

    def _function_tag_handler(self, function_tag: str, template_context: Any):
        ctx: Context = template_context["ctx"]
        render_info: RenderInfo = template_context["render_info"]

        if render_info["group"] != "functions":
            raise TypeError("Inline tags can only be used inside functions.")

        ctx.data.function_tags.merge(
            {function_tag: FunctionTag({"values": [render_info["path"]]})}
        )
