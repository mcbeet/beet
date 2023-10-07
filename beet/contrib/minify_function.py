"""Plugin that minifies function files."""


from beet import Context, Function


def beet_default(ctx: Context):
    for _, function in ctx[Function]:
        function.text = "".join(
            stripped + "\n"
            for line in function.lines
            if (stripped := line.strip()) and not stripped.startswith("#")
        )
