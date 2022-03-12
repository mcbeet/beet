"""Plugin that installs a Jinja extension for easily logging things."""


__all__ = [
    "DbgOptions",
    "DbgRenderer",
    "DbgExtension",
    "get_padding",
]


import json
from dataclasses import dataclass, field
from functools import cached_property
from itertools import cycle
from typing import Any, Dict, List, Tuple

from jinja2.nodes import Node, Output, TemplateData
from pydantic import BaseModel

from beet import Context, JinjaExtension
from beet.core.utils import JsonDict, TextComponent


class DbgOptions(BaseModel):
    command: str = "tellraw @a {payload}"

    enabled: bool = True
    level: str = "info"

    level_config: List[Tuple[str, str]] = [
        ("critical", "dark_red"),
        ("error", "red"),
        ("warn", "yellow"),
        ("info", "gray"),
        ("debug", "green"),
    ]

    preview_digit_width: int = 6
    preview_line_limit: int = 45
    preview_padding: int = 2

    accessor_format: TextComponent = (
        "{{ display_name or target }} for {{ name }} = {{ accessor }}"
    )

    payload: TextComponent = [
        {
            "text": "",
            "hoverEvent": {
                "action": "show_text",
                "contents": [
                    "",
                    {"text": "{{ render_path }} ", "color": "aqua"},
                    {"text": "({{ mode }})\n\n", "color": "dark_aqua"},
                    "{{ preview }}",
                ],
            },
        },
        [
            {
                "text": "[{{ level.upper() }} | {{ project_id }}]: ",
                "color": "{{ level_color }}",
            }
        ],
        {
            "text": "",
            "color": "gold",
            "extra": ["{{ output }}"],
        },
    ]


def beet_default(ctx: Context):
    ctx.template.env.add_extension(DbgExtension)


def get_padding(pixels: int) -> TextComponent:
    """Generate a sequence of bold and normal spaces matching the given number of pixels."""
    if pixels < 12 and pixels not in [4, 5, 8, 9, 10]:
        raise ValueError(f"Invalid number of pixels {pixels}.")

    regular, bold = divmod(pixels, 4)
    regular -= bold

    return [{"text": " " * regular}, {"text": " " * bold, "bold": True}]


@dataclass
class DbgRenderer:
    """Class responsible for rendering dbg statements."""

    ctx: Context

    accessors: JsonDict = field(
        default_factory=lambda: {
            "score": {"score": {"name": "{{ name }}", "objective": "{{ target }}"}},
            "storage": {"storage": "{{ target }}", "nbt": "{{ name }}"},
            "entity": {"entity": "{{ target }}", "nbt": "{{ name }}"},
            "block": {"block": "{{ target }}", "nbt": "{{ name }}"},
        }
    )

    default_level: str = "info"
    default_color: str = "gray"

    @cached_property
    def opts(self) -> DbgOptions:
        return self.ctx.validate("dbg", DbgOptions)

    @cached_property
    def level_colors(self) -> Dict[str, str]:
        return dict(self.opts.level_config)

    @cached_property
    def level_ranks(self) -> Dict[str, int]:
        return {
            level: len(self.opts.level_config) - i
            for i, (level, _) in enumerate(self.opts.level_config)
        }

    def render_preview(self, path: str, lineno: int) -> TextComponent:
        """Render the preview as a text component."""
        function = self.ctx.data.functions[path]
        lines = function.text.splitlines()

        preview_start = max(lineno - 1 - self.opts.preview_padding, 0)
        preview = lines[preview_start : lineno + self.opts.preview_padding]

        numbers = [
            str(i + 1) for i in range(preview_start, preview_start + len(preview))
        ]
        number_width = max(len(n) for n in numbers)

        output: List[TextComponent] = [""]

        for number, line, color in zip(numbers, preview, cycle(["#dddddd", "gray"])):
            if len(line) > self.opts.preview_line_limit:
                line = line[: self.opts.preview_line_limit - 4] + "..."

            padding = number_width - len(number)
            output.extend(get_padding(padding * self.opts.preview_digit_width + 4))
            output.append(
                {
                    "text": number,
                    "color": "red" if int(number) == lineno else "dark_red",
                }
            )

            output.append({"text": " |  ", "color": "dark_gray"})
            output.append({"text": f"{line}\n", "color": color})

        return {"text": "", "extra": output}

    def render(
        self,
        level: str,
        mode: str,
        name: str,
        target: str,
        path: str,
        lineno: int,
    ) -> str:
        """Return the formatted command."""
        if not level:
            level = self.default_level

        if not (
            self.opts.enabled
            and self.level_ranks.get(level, 0)
            >= self.level_ranks.get(self.opts.level, 0)
        ):
            return "\n"

        preview = json.dumps(self.render_preview(path, lineno))

        kwargs = {
            "level": level,
            "level_color": self.level_colors.get(level, self.default_color),
            "mode": mode,
            "name": name,
            "target": target,
            "lineno": lineno,
            "preview": '",' + preview + ',"',
        }

        if mode == "score":
            if scoreboard_data := self.ctx.meta.get("generate_scoreboard"):
                if entry := scoreboard_data.get(target):
                    if display_name := entry.partition(" ")[-1]:
                        kwargs["display_name"] = '",' + display_name + ',"'

        if mode != "print":
            accessor = self.ctx.template.render_json(self.accessors[mode], **kwargs)
            kwargs["accessor"] = '",' + json.dumps(accessor) + ',"'

            output = self.ctx.template.render_string(
                json.dumps(self.opts.accessor_format), **kwargs
            )
        else:
            output = json.dumps(name)

        kwargs["output"] = '",' + output + ',"'
        payload = self.ctx.template.render_string(
            json.dumps(self.opts.payload), **kwargs
        )

        return self.opts.command.format(payload=payload) + "\n"


class DbgExtension(JinjaExtension):
    """A Jinja extension for easily logging things."""

    tags = {"dbg"}

    def parse(self, parser: Any) -> Node:
        renderer = self.ctx.inject(DbgRenderer)

        lineno = next(parser.stream).lineno

        level = next(parser.stream)
        if level.test_any(*[f"name:{level}" for level in renderer.level_ranks]):
            mode = next(parser.stream)
        else:
            mode = level
            level = None

        name = parser.parse_expression()
        target = None

        if mode.test_any("name:score", "name:storage", "name:entity", "name:block"):
            parser.stream.expect("comma")
            target = parser.parse_expression()
        elif not mode.test("name:print"):
            parser.fail(f"Invalid mode {mode.value!r}.", mode.lineno)

        return Output(
            [
                self.call_method(
                    "_dbg_handler",
                    [
                        TemplateData(level.value if level else ""),
                        TemplateData(mode.value),
                        name,
                        target if target else TemplateData(""),
                        TemplateData(lineno),
                    ],
                    lineno=lineno,
                )
            ],
            lineno=lineno,
        )

    def _dbg_handler(
        self,
        level: str,
        mode: str,
        name: str,
        target: str,
        lineno: int,
    ) -> str:
        if self.ctx.meta["render_group"] != "functions":
            raise TypeError("Debug statements can only be used inside functions.")

        renderer = self.ctx.inject(DbgRenderer)
        return renderer.render(
            level,
            mode,
            name,
            target,
            self.ctx.meta["render_path"],
            lineno,
        )
