"""Plugin that minifies function files."""


from beet import Context


def beet_default(ctx: Context):
    for function in ctx.data.functions.values():
        function.text = "".join(
            stripped + "\n"
            for line in function.lines
            if (stripped := line.strip()) and not stripped.startswith("#")
        )
