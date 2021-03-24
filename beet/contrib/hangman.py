"""Plugin that allows hanging indents to spread commands on multiple lines."""


__all__ = [
    "fold_hanging_commands",
]


from typing import List

from beet import Context


def beet_default(ctx: Context):
    for function in ctx.data.functions.values():
        function.lines = fold_hanging_commands(function.lines)


def fold_hanging_commands(lines: List[str]) -> List[str]:
    """Fold hanging commands on a single line."""
    result = []
    current, *lines = lines
    indentation = 0
    hanging_blank_lines = 0

    for line in lines:
        stripped = line.lstrip()

        if stripped:
            indentation = len(line) - len(stripped)

        if indentation > 0:
            if stripped.startswith("#"):
                result.append(stripped)
            elif stripped:
                hanging_blank_lines = 0
                current += " " + stripped
            else:
                hanging_blank_lines += 1
        else:
            result.append(current)
            result.extend([""] * hanging_blank_lines)
            current = stripped

    result.append(current)

    return result
