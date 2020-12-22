"""Plugin that installs a Jinja extension for declaring function tags inline."""


__all__ = [
    "InlineFunctionTags",
]


from typing import Any

from jinja2.ext import Extension
from jinja2.nodes import DerivedContextReference  # type: ignore
from jinja2.nodes import ExprStmt, Node

from beet import Context, FunctionTag
from beet.core.utils import JsonDict


def beet_default(ctx: Context):
    ctx.template.env.add_extension(InlineFunctionTags)


class InlineFunctionTags(Extension):
    """A Jinja extension that allows you to declare function tags inline."""

    tags = {"tag"}

    def parse(self, parser: Any) -> Node:
        lineno = next(parser.stream).lineno

        args = [DerivedContextReference(), parser.parse_expression()]

        handler = self.call_method("_function_tag_handler", args, lineno=lineno)
        return ExprStmt(handler, lineno=lineno)

    def _function_tag_handler(self, context: Any, function_tag: str):
        ctx: Context = context["ctx"]
        render: JsonDict = context["__render__"]

        if render["group"] != "functions":
            raise TypeError("Inline tags can only be used inside functions.")

        ctx.data.function_tags.merge(
            {function_tag: FunctionTag({"values": [render["path"]]})}
        )
