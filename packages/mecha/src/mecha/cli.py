__all__ = [
    "validate",
    "mecha",
    "main",
]


import logging
import os
import zipfile
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Optional, Tuple

import click
from beet import LATEST_MINECRAFT_VERSION, Context, DataPack, Function, run_beet
from beet.core.utils import resolve_within, split_version
from beet.toolchain.cli import BeetCommand, LogHandler, error_handler, message_fence

from mecha import __version__

from .api import Mecha
from .diagnostic import Diagnostic


@contextmanager
def report_decode_errors(mc: Mecha, filename: str) -> Iterator[None]:
    """Report a file that is not valid utf-8 as a diagnostic instead of crashing."""
    # AI-assisted fix (Claude, Anthropic): see the commit message.
    try:
        yield
    except UnicodeDecodeError as exc:
        mc.diagnostics.add(
            Diagnostic(
                "error",
                f"Could not decode a file as utf-8: {exc.reason}.",
                filename=filename,
            )
        )


def check_minecraft_version(
    ctx: click.Context, param: click.Parameter, value: str
) -> str:
    """Reject values that cannot be parsed as a version number."""
    # AI-assisted fix (Claude, Anthropic): see the commit message.
    try:
        split_version(value)
    except ValueError:
        raise click.BadParameter(
            f"{value!r} is not a valid Minecraft version."
        ) from None
    return value


def validate(ctx: Context):
    """Plugin for running mecha on the provided sources."""
    mc = ctx.inject(Mecha)

    for path in ctx.meta["source"]:
        path = ctx.directory / path

        if zipfile.is_zipfile(path) or (path / "data").is_dir():
            with report_decode_errors(mc, str(resolve_within(path, ctx.directory))):
                mc.compile(DataPack(path=path), report=mc.diagnostics)

        elif path.is_dir():
            for filename in sorted(path.glob("**/*.mcfunction")):
                with report_decode_errors(
                    mc, str(resolve_within(filename, ctx.directory))
                ):
                    mc.compile(Function(source_path=filename), report=mc.diagnostics)

        elif path.is_file():
            with report_decode_errors(mc, str(resolve_within(path, ctx.directory))):
                mc.compile(Function(source_path=path), report=mc.diagnostics)


@click.command(
    cls=BeetCommand,
    context_settings={"help_option_names": ("-h", "--help")},
)
@click.argument("source", nargs=-1, type=click.Path(exists=True))
@click.option(
    "-m",
    "--minecraft",
    metavar="VERSION",
    default=LATEST_MINECRAFT_VERSION,
    callback=check_minecraft_version,
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
    help="Write statistics to a json file (collects statistics).",
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
        # AI-assisted fix (Claude, Anthropic): see the commit message.
        "require": ["mecha.contrib.statistics"] if stats or json else [],
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
