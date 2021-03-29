"""Plugin that installs a Jinja extension for declaring function tags inline."""


__all__ = [
    "InlineFunctionTags",
]


from typing import Any, List

from jinja2.ext import Extension
from jinja2.nodes import DerivedContextReference  # type: ignore
from jinja2.nodes import ExprStmt, Node

from beet import Context, FunctionTag


def beet_default(ctx: Context):
    ctx.template.env.add_extension(InlineFunctionTags)  # type: ignore


class InlineFunctionTags(Extension):
    """A Jinja extension that allows you to declare function tags inline."""

    tags = {"tag"}

    def parse(self, parser: Any) -> Node:
        lineno = next(parser.stream).lineno

        args: List[Any] = [DerivedContextReference(), parser.parse_expression()]

        return ExprStmt(
            self.call_method("_function_tag_handler", args, lineno=lineno),  # type: ignore
            lineno=lineno,
        )

    def _function_tag_handler(self, context: Any, function_tag: str):
        ctx: Context = context["ctx"]

        if ctx.meta["render_group"] != "functions":
            raise TypeError("Inline tags can only be used inside functions.")

        ctx.data.function_tags.merge(
            {function_tag: FunctionTag({"values": [ctx.meta["render_path"]]})}
        )
