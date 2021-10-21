"""Plugin that installs a Jinja extension for easily logging things in commands."""


__all__ = [
    "DbgOptions",
    "DbgRenderer",
    "DbgExtension",
]


import json
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any, List

from jinja2.nodes import Node, Output, TemplateData
from pydantic import BaseModel

from beet import Context, JinjaExtension
from beet.core.utils import JsonDict, TextComponent


class DbgOptions(BaseModel):
    command: str = "tellraw @a {payload}"
    payload: List[TextComponent] = [
        {
            "text": "",
            "hoverEvent": {
                "action": "show_text",
                "contents": [
                    {"text": "Type: {{ mode | title }}\n", "color": "gray"},
                    {"text": "Path: {{ render_path }}\n", "color": "gray"},
                    {"text": "Lineno: {{ lineno }}", "color": "gray"},
                ],
            },
        },
        {"text": "[{{ project_id }}]: ", "color": "gray"},
        {
            "text": "< {{ name }} ",
            "color": "gold",
            "extra": ["{{ accessor }}", " >"],
        },
    ]


def beet_default(ctx: Context):
    ctx.template.env.add_extension(DbgExtension)


@dataclass
class DbgRenderer:
    """Class responsible for formatting the json text of a dbg statement."""

    ctx: Context

    accessors: JsonDict = field(
        default_factory=lambda: {
            "score": {"score": {"name": "{{name}}", "objective": "{{target}}"}},
            "storage": {"storage": "{{target}}", "nbt": "{{name}}"},
            "entity": {"entity": "{{target}}", "nbt": "{{name}}"},
            "block": {"block": "{{target}}", "nbt": "{{name}}"},
        }
    )

    @cached_property
    def opts(self) -> DbgOptions:
        return self.ctx.validate("dbg", DbgOptions)

    def render(self, mode: str, name: str, target: str, lineno: int) -> str:
        """Return the json text as a string."""
        kwargs = {
            "mode": mode,
            "name": name,
            "target": target,
            "lineno": lineno,
        }

        accessor = self.ctx.template.render_json(self.accessors[mode], **kwargs)

        return self.ctx.template.render_string(
            json.dumps(self.opts.payload),
            accessor='",' + json.dumps(accessor) + ',"',
            **kwargs,
        )


class DbgExtension(JinjaExtension):
    """A Jinja extension for easily logging things in commands."""

    tags = {"dbg"}

    def parse(self, parser: Any) -> Node:
        lineno = next(parser.stream).lineno

        mode = next(parser.stream)
        if not mode.test_any("name:score", "name:storage", "name:entity", "name:block"):
            parser.fail(f"Invalid mode {mode.value!r}.", mode.lineno)

        name = parser.parse_expression()
        parser.stream.expect("comma")
        target = parser.parse_expression()

        return Output(
            [
                self.call_method(
                    "_dbg_handler",
                    [TemplateData(mode.value), name, target, TemplateData(lineno)],
                    lineno=lineno,
                )
            ],
            lineno=lineno,
        )

    def _dbg_handler(self, mode: str, name: str, target: str, lineno: int) -> str:
        if self.ctx.meta["render_group"] != "functions":
            raise TypeError("Debug statements can only be used inside functions.")

        renderer = self.ctx.inject(DbgRenderer)
        payload = renderer.render(mode, name, target, lineno)

        return renderer.opts.command.format(payload=payload)
