"""Plugin that installs a Jinja extension for declaring function tags inline."""


__all__ = [
    "InlineFunctionTags",
]


from typing import Any, List

from jinja2.nodes import ExprStmt, Node

from beet import Context, FunctionTag, JinjaExtension


def beet_default(ctx: Context):
    ctx.template.env.add_extension(InlineFunctionTags)


class InlineFunctionTags(JinjaExtension):
    """A Jinja extension that allows you to declare function tags inline."""

    tags = {"tag"}

    def parse(self, parser: Any) -> Node:
        lineno = next(parser.stream).lineno
        args: List[Any] = [parser.parse_expression()]

        return ExprStmt(
            self.call_method("_function_tag_handler", args, lineno=lineno),
            lineno=lineno,
        )

    def _function_tag_handler(self, function_tag: str):
        if self.ctx.meta["render_group"] != "functions":
            raise TypeError("Inline tags can only be used inside functions.")

        self.ctx.data.function_tags.merge(
            {function_tag: FunctionTag({"values": [self.ctx.meta["render_path"]]})}
        )
