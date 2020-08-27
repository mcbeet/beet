import click

from . import __version__


def print_version(ctx, _param, value):
    if not value or ctx.resilient_parsing:
        return
    click.secho(f"Beet v{__version__}", fg="red")
    ctx.exit()


@click.group(invoke_without_command=True)
@click.pass_context
@click.option(
    "--version",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=print_version,
    help="Show the version and exit.",
)
def beet(ctx):
    """A python library and toolchain for programmatic Minecraft data packs and resource packs."""
    if ctx.invoked_subcommand:
        return


def main():
    beet(prog_name="beet")
