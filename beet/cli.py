__all__ = ["beet", "main"]


from contextlib import contextmanager
from pathlib import Path
from typing import Sequence, Optional

import click
from click_help_colors import HelpColorsGroup, HelpColorsCommand, version_option

from . import __version__
from .project import GeneratorError, GeneratorImportError
from .toolchain import Toolchain, ErrorMessage
from .utils import format_exc, format_obj


class ShorthandGroup(HelpColorsGroup):
    def get_command(self, ctx: click.Context, cmd_name: str) -> Optional[click.Command]:
        if command := super().get_command(ctx, cmd_name):
            return command

        matches = [cmd for cmd in self.list_commands(ctx) if cmd.startswith(cmd_name)]

        if len(matches) > 1:
            match_list = ", ".join(sorted(matches))
            ctx.fail(f"Ambiguous shorthand {cmd_name!r} ({match_list}).")
        elif matches:
            return super().get_command(ctx, matches[0])
        else:
            return None


@click.group(
    cls=ShorthandGroup,
    help_headers_color="yellow",
    help_options_color="red",
    invoke_without_command=True,
)
@click.pass_context
@click.option(
    "-C",
    "--directory",
    type=click.Path(exists=True, file_okay=False),
    help="The project directory.",
)
@version_option(
    version=__version__,
    prog_name="Beet",
    message="%(prog)s v%(version)s",
    prog_name_color="red",
    message_color="yellow",
)
def beet(ctx: click.Context, directory: str):
    """The Beet toolchain.

    The `build` command will build the project in the current directory.
    It's also the default command so invoking `beet` without any
    arguments will work exactly as if you used the `build` command
    directly:

        $ beet

    You can use the `init` command to initialize a new project in the
    current directory:

        $ beet init
    """
    ctx.obj = Toolchain(directory)

    if not ctx.invoked_subcommand:
        ctx.invoke(build)


def display_error(message: str, exception: BaseException = None):
    click.secho("Error: " + message, fg="red", bold=True)
    if exception:
        click.echo("\n" + format_exc(exception), nl=False)


@contextmanager
def toolchain_operation(ctx: click.Context, title: str):
    click.secho(title + "\n", fg="yellow")

    try:
        yield
    except ErrorMessage as exc:
        display_error(" ".join(exc.args))
    except GeneratorImportError as exc:
        generator = format_obj(exc.args[0])
        display_error(f"Couldn't import generator {generator}.", exc.__cause__)
    except GeneratorError as exc:
        generator = format_obj(exc.args[0])
        display_error(f"Generator {generator} raised an exception.", exc.__cause__)
    except click.Abort:
        click.echo()
        display_error(f"Aborted.")
    except Exception as exc:
        display_error("An unhandled exception occurred. This could be a bug.", exc)
    else:
        click.secho("Done!", fg="green", bold=True)
        return

    ctx.exit(1)


@beet.command(cls=HelpColorsCommand)
@click.pass_context
def build(ctx: click.Context):
    """Build the project in the current directory."""
    with toolchain_operation(ctx, "Building project..."):
        ctx.obj.build_project()


@beet.command(cls=HelpColorsCommand)
@click.pass_context
def watch(ctx: click.Context):
    """Watch for file changes and rebuild the current project."""
    with toolchain_operation(ctx, "Watching project..."):
        for change in ctx.obj.watch_project():
            ctx.obj.build_project()


@beet.command(cls=HelpColorsCommand)
@click.pass_context
@click.argument("cache_name", nargs=-1)
@click.option(
    "-c",
    "--clear",
    is_flag=True,
    help="Clear the entire cache directory or the selected caches.",
)
def cache(ctx: click.Context, cache_name: Sequence[str], clear: bool):
    """Inspect or clear the selected caches."""
    cache_list = ", ".join(cache_name or ["all caches"])

    if clear:
        with toolchain_operation(ctx, f"Clearing {cache_list}..."):
            ctx.obj.clear_cache(cache_name)
    else:
        with toolchain_operation(ctx, f"Inspecting {cache_list}..."):
            click.echo(ctx.obj.inspect_cache(cache_name))


@beet.command(cls=HelpColorsCommand)
@click.pass_context
def init(ctx: click.Context):
    """Initialize a new project in the current directory."""
    with toolchain_operation(ctx, "Initializing new project..."):
        ctx.obj.init_project()


def main():
    beet(prog_name="beet")
