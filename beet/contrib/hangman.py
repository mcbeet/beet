"""Plugin that allows hanging indents to spread commands on multiple lines."""


__all__ = [
    "fold_hanging_commands",
    "parse_trailing_comment",
]


import re
from typing import List, Optional, Tuple

from beet import Context

REGEX_COMMENT = re.compile(r"(\s+#(?:\s+.*)?$)")
REGEX_QUOTE = re.compile(r"(\"(?:.*?[^\\])?\"|'(?:.*?[^\\])?')")


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
                hanging_blank_lines = 0
            elif stripped:
                stripped, comment = parse_trailing_comment(stripped)
                if comment:
                    result.append(comment)
                current += " " + stripped
                hanging_blank_lines = 0
            else:
                hanging_blank_lines += 1
        else:
            result.append(current)
            result.extend([""] * hanging_blank_lines)
            hanging_blank_lines = 0
            stripped, comment = parse_trailing_comment(stripped)
            if comment:
                result.append(comment)
            current = stripped

    result.append(current)

    return result


def parse_trailing_comment(line: str) -> Tuple[str, Optional[str]]:
    """Split the line and return the extracted trailing comment."""
    chunks = REGEX_QUOTE.split(line)
    result = ""

    while chunks:
        notcomment, *comment = REGEX_COMMENT.split(chunks.pop(0))
        result += notcomment
        if comment:
            return result, comment[0].lstrip() + "".join(chunks)
        if chunks:
            result += chunks.pop(0)

    return result, None
