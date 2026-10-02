"""Plugin that minifies function files."""

from beet import Context, Function


def beet_default(ctx: Context):
    for _, function in ctx[Function]:
        lines = []
        comment_cont = False
        for line in function.lines:
            stripped = line.strip()
            comment = stripped.startswith("#")
            if stripped and not comment and not comment_cont:
                lines.append(stripped + "\n")
            comment_cont = (comment or comment_cont) and stripped.endswith("\\")
        function.text = "".join(lines)
