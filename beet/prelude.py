__all__ = ["load", "preamble"]


from . import __version__
from .project import Context


def load(ctx: Context):
    config = ctx.meta.get("load", {})

    for key, pack in zip(["resource_packs", "data_packs"], ctx.packs):
        cls = type(pack)

        for path in config.get(key, []):
            pack.merge(cls(path=ctx.directory / path))


def preamble(ctx: Context):
    config = ctx.meta.get("preamble", {})

    template = config.get("template")

    if not template and (filename := config.get("file")):
        template = (ctx.directory / filename).read_text()
    if not template:
        return

    isotime = ctx.current_time.isoformat()
    ctime = " ".join(ctx.current_time.ctime().split())

    match = config.get("match", [])
    patterns = [match] if isinstance(match, str) else match

    for name in ctx.data.functions.match(*patterns):
        function = ctx.data.functions[name]

        header = template.format(
            function_name=name,
            isotime=isotime,
            ctime=ctime,
            beet_version=__version__,
        ).splitlines()

        function.content[:0] = header + [""] if function.content else header


def default_generator(ctx: Context):
    ctx.apply(load)
    ctx.queue.append(preamble)
