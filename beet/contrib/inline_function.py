"""Plugin that installs a Jinja extension for declaring functions inline."""


__all__ = [
    "InlineFunctions",
]


from typing import Any

from jinja2.ext import Extension
from jinja2.nodes import DerivedContextReference  # type: ignore
from jinja2.nodes import CallBlock, Name, Node

from beet import Context, Function
from beet.core.utils import JsonDict


def beet_default(ctx: Context):
    ctx.template.env.add_extension(InlineFunctions)


class InlineFunctions(Extension):
    """A Jinja extension that allows you to declare functions inline."""

    tags = {"function"}

    def parse(self, parser: Any) -> Node:
        lineno = next(parser.stream).lineno

        args = [DerivedContextReference(), parser.parse_expression()]
        body = parser.parse_statements(["name:endfunction"], drop_needle=True)

        handler = self.call_method("_function_handler", args)
        render = Name("__render__", "param")
        return CallBlock(handler, [render], [], body).set_lineno(lineno)

    def _function_handler(self, context: Any, path: str, caller: Any) -> str:
        ctx: Context = context["ctx"]
        render: JsonDict = context.get("__render__", {})

        commands = caller(dict(render, path=path, group="functions"))
        ctx.data[path] = Function(commands)
        return ""
