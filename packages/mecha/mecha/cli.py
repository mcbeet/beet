__all__ = [
    "validate",
    "mecha",
    "main",
]


import logging
import os
import zipfile
from typing import Optional, Tuple

import click
from beet import LATEST_MINECRAFT_VERSION, Context, DataPack, Function, run_beet
from beet.toolchain.cli import BeetCommand, LogHandler, error_handler, message_fence

from mecha import __version__

from .api import Mecha


def validate(ctx: Context):
    """Plugin for running mecha on the provided sources."""
    mc = ctx.inject(Mecha)

    for path in ctx.meta["source"]:
        path = ctx.directory / path

        if zipfile.is_zipfile(path) or (path / "data").is_dir():
            mc.compile(DataPack(path=path), report=mc.diagnostics)

        elif path.is_dir():
            for filename in path.glob("**/*.mcfunction"):
                mc.compile(Function(source_path=filename), report=mc.diagnostics)

        elif path.is_file():
            mc.compile(Function(source_path=path), report=mc.diagnostics)


@click.command(  # type: ignore
    cls=BeetCommand,
    context_settings={"help_option_names": ("-h", "--help")},
)
@click.argument("source", nargs=-1, type=click.Path(exists=True))
@click.option(
    "-m",
    "--minecraft",
    metavar="VERSION",
    default=LATEST_MINECRAFT_VERSION,
    help="Minecraft version.",
)
@click.option(
    "-l",
    "--log",
    metavar="LEVEL",
    type=click.Choice(
        ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
        case_sensitive=False,
    ),
    default="WARNING",
    help="Configure output verbosity.",
)
@click.option(
    "-s",
    "--stats",
    is_flag=True,
    help="Collect statistics.",
)
@click.option(
    "-j",
    "--json",
    metavar="FILENAME",
    help="Output json.",
)
@click.version_option(
    __version__,
    "-v",
    "--version",
    message=click.style("%(prog)s", fg="red")
    + click.style(" v%(version)s", fg="green"),
)
@error_handler(should_exit=True)
def mecha(
    source: Tuple[str, ...],
    minecraft: str,
    log: str,
    stats: bool,
    json: Optional[str],
):
    """Validate data packs and .mcfunction files."""
    if stats and log != "DEBUG":
        log = "INFO"

    logger = logging.getLogger()
    logger.setLevel(log)
    logger.addHandler(LogHandler())

    config = {
        "minecraft": minecraft,
        "require": stats * ["mecha.contrib.statistics"],
        "pipeline": ["mecha.cli.validate"],
        "meta": {
            "source": source,
            "mecha": {
                "readonly": True,
                "cache": False,
            },
            "statistics": {
                "output": os.path.abspath(json) if json else None,
            },
        },
    }

    with message_fence(f"Validating with mecha v{__version__}"):
        if source:
            with run_beet(config):
                pass
        else:
            logger.warning("No path provided.", extra={"prefix": "mecha"})
            logger.warning("Use --help to see usage.", extra={"prefix": "mecha"})


def main():
    """Invoke the command-line entrypoint."""
    mecha(prog_name="mecha")
