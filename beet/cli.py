__all__ = ["beet", "main"]


import json
import time
from contextlib import contextmanager
from functools import partial
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


def display_error(message: str, exception: BaseException = None, padding: int = 0):
    click.secho("\n" * padding + "Error: " + message, fg="red", bold=True)
    if exception:
        click.echo("\n" + format_exc(exception), nl=False)
    click.echo("\n" * padding, nl=False)


@contextmanager
def toolchain_operation(ctx: click.Context, title: str = None):
    if title:
        click.secho(title + "\n", fg="yellow")

    err = partial(display_error, padding=int(not title))

    try:
        yield
    except ErrorMessage as exc:
        err(" ".join(exc.args))
    except GeneratorImportError as exc:
        generator = format_obj(exc.args[0])
        err(f"Couldn't import generator {generator}.", exc.__cause__)
    except GeneratorError as exc:
        generator = format_obj(exc.args[0])
        err(f"Generator {generator} raised an exception.", exc.__cause__)
    except (click.Abort, KeyboardInterrupt):
        click.echo()
        err("Aborted.")
    except json.JSONDecodeError as exc:
        err("Attempted to decode invalid json.", exc)
    except Exception as exc:  # pylint: disable=broad-except
        err("An unhandled exception occurred. This could be a bug.", exc)
    else:
        if title:
            click.secho("Done!", fg="green", bold=True)
        return

    if title:
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
        for changes in ctx.obj.watch_project():
            filename, action = next(iter(changes.items()))

            text = (
                f"{action.capitalize()} {filename!r}"
                if changes == {filename: action}
                else f"{len(changes)} changes detected"
            )

            now = time.strftime("%H:%M:%S")
            change_time = click.style(now, fg="green", bold=True)
            click.echo(f"{change_time} {text}")

            with toolchain_operation(ctx):
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
@click.argument("directory", required=False)
@click.option(
    "-c",
    "--clear",
    is_flag=True,
    help="Clear the link between the current project and Minecraft.",
)
def link(ctx: click.Context, directory: Optional[str], clear: bool):
    """Link the generated resource pack and data pack to Minecraft."""
    if clear:
        with toolchain_operation(ctx, "Clearing project link..."):
            ctx.obj.clear_project_link()
    else:
        with toolchain_operation(ctx, "Linking project..."):
            assets, data = ctx.obj.link_project(directory)
            report = "\n".join(
                f"{title}:\n  │  destination = {pack_dir}\n"
                for title, pack_dir in [("Resource pack", assets), ("Data pack", data)]
                if pack_dir
            )
            click.echo(report)


@beet.command(cls=HelpColorsCommand)
@click.pass_context
@click.option("--name", help="The name of the project.")
@click.option("--description", help="The description of the project.")
@click.option("--author", help="The author of the project.")
@click.option("--version", help="The version of the project.")
@click.option("-y", "--yes", is_flag=True, help="Confirm new project settings.")
def init(
    ctx: click.Context,
    name: Optional[str],
    description: Optional[str],
    author: Optional[str],
    version: Optional[str],
    yes: bool,
):
    """Initialize a new project in the current directory."""
    with toolchain_operation(ctx, "Initializing new project..."):
        if yes:
            name = name or Path.cwd().name
            description = description or "Generated by Beet"
            author = author or "Unknown"
            version = version or "0.0.0"
        else:
            user_prompts = not all([name, description, author, version])

            name = name or click.prompt("Project name", Path.cwd().name)
            description = description or click.prompt(
                "Project description", "Generated by Beet"
            )
            author = author or click.prompt("Project author", "Unknown")
            version = version or click.prompt("Project version", "0.0.0")

            if user_prompts:
                click.echo()

            config = Path(ctx.obj.initial_directory, Toolchain.PROJECT_CONFIG_FILE)
            click.echo("About to create " + click.style(str(config), fg="red") + ".\n")

            if not click.confirm("Is this ok?", default=True):
                raise click.Abort()

            click.echo()

        ctx.obj.init_project(name, description, author, version)


def main():
    # pylint: disable=unexpected-keyword-arg,no-value-for-parameter
    beet(prog_name="beet")
