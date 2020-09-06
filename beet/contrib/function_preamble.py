__all__ = ["default_generator"]


import re

from beet import Context, __version__


def default_generator(ctx: Context):
    preamble = ctx.meta.get("preamble")
    if not preamble and (preamble_file := ctx.meta.get("preamble_file")):
        preamble = (ctx.directory / preamble_file).read_text()

    if not preamble:
        return

    regex = re.compile(ctx.meta.get("preamble_match", ".+"))

    isotime = ctx.current_time.isoformat()
    ctime = " ".join(ctx.current_time.ctime().split())

    for name, function in ctx.data.functions.items():
        if not regex.match(name):
            continue

        header = preamble.format(
            function_name=name,
            isotime=isotime,
            ctime=ctime,
            beet_version=__version__,
        ).splitlines()

        if function.content:
            header.append("")

        function.content[:0] = header
