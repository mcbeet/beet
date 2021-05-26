"""Plugin that installs a Jinja extension for declaring functions inline."""


__all__ = [
    "InlineFunctions",
]


from typing import Any, List

from jinja2.nodes import CallBlock, Node, TemplateData

from beet import Context, Function, JinjaExtension


def beet_default(ctx: Context):
    ctx.template.env.add_extension(InlineFunctions)


class InlineFunctions(JinjaExtension):
    """A Jinja extension that allows you to declare functions inline."""

    tags = {"function"}

    def parse(self, parser: Any) -> Node:
        lineno = next(parser.stream).lineno
        args: List[Any] = [parser.parse_expression()]

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
            self.call_method("_function_handler", args, lineno=lineno),
            [],
            [],
            body,
            lineno=lineno,
        )

    def _function_handler(self, path: str, op: str, caller: Any) -> str:
        if (
            path == self.ctx.meta.get("render_path")
            and self.ctx.meta.get("render_group") == "functions"
        ):
            return caller()

        with self.ctx.override(render_path=path, render_group="functions"):
            commands = caller()

        function = Function(commands)

        if op == "replace":
            self.ctx.data[path] = function
        elif op == "append":
            self.ctx.data.functions.setdefault(path, Function()).append(function)
        elif op == "prepend":
            self.ctx.data.functions.setdefault(path, Function()).prepend(function)

        return ""
