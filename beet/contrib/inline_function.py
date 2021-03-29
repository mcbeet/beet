"""Plugin that installs a Jinja extension for declaring functions inline."""


__all__ = [
    "InlineFunctions",
]


from typing import Any, List

from jinja2.ext import Extension
from jinja2.nodes import DerivedContextReference  # type: ignore
from jinja2.nodes import CallBlock, Node

from beet import Context, Function


def beet_default(ctx: Context):
    ctx.template.env.add_extension(InlineFunctions)  # type: ignore


class InlineFunctions(Extension):
    """A Jinja extension that allows you to declare functions inline."""

    tags = {"function"}

    def parse(self, parser: Any) -> Node:
        lineno = next(parser.stream).lineno

        args: List[Any] = [DerivedContextReference(), parser.parse_expression()]
        body = parser.parse_statements(["name:endfunction"], drop_needle=True)

        return CallBlock(
            self.call_method("_function_handler", args, lineno=lineno),  # type: ignore
            [],
            [],
            body,
            lineno=lineno,
        )

    def _function_handler(self, context: Any, path: str, caller: Any) -> str:
        ctx: Context = context["ctx"]

        with ctx.override(render_path=path, render_group="functions"):
            commands = caller()

        ctx.data[path] = Function(commands)
        return ""
