"""Plugin that installs a Jinja extension for declaring functions inline."""


__all__ = [
    "InlineFunctions",
]


from typing import Any, List

from jinja2.ext import Extension
from jinja2.nodes import DerivedContextReference  # type: ignore
from jinja2.nodes import CallBlock, Node, TemplateData

from beet import Context, Function


def beet_default(ctx: Context):
    ctx.template.env.add_extension(InlineFunctions)  # type: ignore


class InlineFunctions(Extension):
    """A Jinja extension that allows you to declare functions inline."""

    tags = {"function"}

    def parse(self, parser: Any) -> Node:
        lineno = next(parser.stream).lineno

        args: List[Any] = [DerivedContextReference(), parser.parse_expression()]

        if parser.stream.current.test("name:append"):
            args.append(TemplateData("append"))
            parser.stream.skip()
        elif parser.stream.current.test("name:prepend"):
            args.append(TemplateData("prepend"))
            parser.stream.skip()
        else:
            args.append(TemplateData("replace"))

        body = parser.parse_statements(["name:endfunction"], drop_needle=True)

        return CallBlock(
            self.call_method("_function_handler", args, lineno=lineno),  # type: ignore
            [],
            [],
            body,
            lineno=lineno,
        )

    def _function_handler(self, context: Any, path: str, op: str, caller: Any) -> str:
        ctx: Context = context["ctx"]

        with ctx.override(render_path=path, render_group="functions"):
            commands = caller()

        if op == "replace":
            ctx.data[path] = Function(commands)
        elif op == "append":
            ctx.data.functions.setdefault(path, Function()).append(Function(commands))
        elif op == "prepend":
            ctx.data.functions.setdefault(path, Function()).prepend(Function(commands))

        return ""
