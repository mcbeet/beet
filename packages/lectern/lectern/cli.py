__all__ = [
    "lectern",
    "main",
]


from typing import Any, Optional, Tuple

import click
from beet import run_beet
from beet.toolchain.cli import error_handler

from lectern import __version__


@click.command(context_settings={"help_option_names": ("-h", "--help")})
@click.pass_context
@click.argument("path", nargs=-1)
@click.option(
    "-d",
    "--data-pack",
    metavar="<path>",
    help="Extract data pack.",
)
@click.option(
    "-r",
    "--resource-pack",
    metavar="<path>",
    help="Extract resource pack.",
)
@click.option(
    "-e",
    "--external-files",
    metavar="<path>",
    help="Emit external files.",
)
@click.version_option(
    __version__,
    "-v",
    "--version",
    message="%(prog)s v%(version)s",
)
@error_handler(should_exit=True)
def lectern(
    ctx: click.Context,
    path: Tuple[str],
    data_pack: Optional[str],
    resource_pack: Optional[str],
    external_files: Optional[str],
):
    """Literate Minecraft data packs and resource packs."""
    config: Any

    if data_pack or resource_pack:
        config = {
            "pipeline": ["lectern"],
            "meta": {
                "lectern": {"load": list(path)},
            },
        }
    else:
        try:
            *packs, dest = path
        except ValueError:
            click.echo(ctx.get_help())
            ctx.exit(1)
        config = {
            "data_pack": {"load": packs},
            "resource_pack": {"load": packs},
            "pipeline": ["lectern"],
            "meta": {
                "lectern": {"snapshot": dest, "external_files": external_files},
            },
        }

    with run_beet(config) as beet_ctx:
        if data_pack:
            beet_ctx.data.save(path=data_pack, overwrite=True)
        if resource_pack:
            beet_ctx.assets.save(path=resource_pack, overwrite=True)


def main():
    """Invoke the command-line entrypoint."""
    lectern(prog_name="lectern")  # type: ignore
