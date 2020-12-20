__all__ = [
    "main",
    "beet",
]


import time
from contextlib import contextmanager
from typing import Any, Optional, Sequence, TypeVar

import click
from click.decorators import pass_context
from click_help_colors import HelpColorsGroup

from beet import __version__

from .config import InvalidProjectConfig
from .pipeline import PluginError, PluginImportError
from .project import ErrorMessage, Project
from .template import TemplateError
from .utils import format_exc, format_obj

T = TypeVar("T")

pass_project = click.make_pass_decorator(Project, ensure=True)


class CustomGroup(HelpColorsGroup):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(
            *args,
            **kwargs,
            invoke_without_command=True,
            context_settings={"help_option_names": ("-h", "--help")},
            help_headers_color="red",
            help_options_color="green",
        )

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

    def format_usage(self, ctx: click.Context, formatter: Any):
        formatter.write_usage(
            ctx.command_path,
            " ".join(self.collect_usage_pieces(ctx)),
            click.style("Usage", fg="red") + ": ",
        )


@click.group(cls=CustomGroup)
@pass_project
@pass_context
@click.option(
    "-d",
    "--directory",
    type=click.Path(exists=True, file_okay=False),
    help="Use the specified project directory.",
)
@click.option(
    "-c",
    "--config",
    type=click.Path(exists=True, dir_okay=False),
    help="Use the specified config file.",
)
@click.version_option(
    __version__,
    "-v",
    "--version",
    message=click.style("%(prog)s", fg="red")
    + click.style(" v%(version)s", fg="green"),
)
def beet(
    ctx: click.Context,
    project: Project,
    directory: Optional[str],
    config: Optional[str],
):
    """The beet toolchain."""
    if config:
        project.config_path = config
    elif directory:
        project.config_directory = directory

    if not ctx.invoked_subcommand:
        ctx.invoke(build)  # type: ignore


def format_error(
    message: str, exception: Optional[BaseException] = None, padding: int = 0
) -> str:
    output = "\n" * padding
    output += click.style("Error: " + message, fg="red", bold=True) + "\n"
    if exception:
        output += "\n" + format_exc(exception)
    output += "\n" * padding
    return output


@contextmanager
def error_handler(should_exit: bool = False, format_padding: int = 0):
    exception = None

    try:
        yield
    except ErrorMessage as exc:
        message = " ".join(exc.args)
    except PluginImportError as exc:
        message = f"Couldn't import plugin {format_obj(exc.args[0])}."
        exception = exc.__cause__
    except PluginError as exc:
        message = f"Plugin {format_obj(exc.args[0])} raised an exception."
        exception = exc.__cause__
    except (click.Abort, KeyboardInterrupt):
        click.echo()
        message = "Aborted."
    except InvalidProjectConfig as exc:
        message = f"Couldn't load config file.\n\n{exc}"
    except TemplateError as exc:
        message = " ".join(exc.args)
        exception = exc.__cause__
    except Exception as exc:
        message = "An unhandled exception occurred. This could be a bug."
        exception = exc
    else:
        return

    click.echo(format_error(message, exception, format_padding), nl=False)

    if should_exit:
        raise click.exceptions.Exit(1)


@contextmanager
def message_fence(message: str):
    click.secho(message + "\n", fg="red")  # type: ignore
    yield
    click.secho("Done!", fg="green", bold=True)  # type: ignore


def command(func: T) -> T:
    return beet.command()(pass_project(error_handler(should_exit=True)(func)))  # type: ignore


@command
@click.option(
    "-l",
    "--link",
    metavar="TARGET",
    help="Link the project before building.",
)
def build(project: Project, link: Optional[str]):
    """Build the current project."""
    text = "Linking and building project..." if link else "Building project..."
    with message_fence(text):
        if link:
            click.echo("\n".join(project.link(target=link)))
        project.build()


@command
@click.option(
    "-l",
    "--link",
    metavar="TARGET",
    help="Link the project before watching.",
)
@click.option(
    "-i",
    "--interval",
    metavar="SECONDS",
    default=0.6,
    help="Configure the polling interval.",
)
def watch(project: Project, link: Optional[str], interval: float):
    """Watch the project directory and build on file changes."""
    text = "Linking and watching project..." if link else "Watching project..."
    with message_fence(text):
        if link:
            click.echo("\n".join(project.link(target=link)))

        for changes in project.watch(interval):
            filename, action = next(iter(changes.items()))

            text = (
                f"{action.capitalize()} {filename!r}"
                if changes == {filename: action}
                else f"{len(changes)} changes detected"
            )

            now = time.strftime("%H:%M:%S")
            change_time = click.style(now, fg="green", bold=True)
            click.echo(f"{change_time} {text}")

            with error_handler(format_padding=1):
                project.build()


@command
@click.argument("patterns", nargs=-1)
@click.option(
    "-c",
    "--clear",
    is_flag=True,
    help="Clear the cache.",
)
def cache(project: Project, patterns: Sequence[str], clear: bool):
    """Inspect or clear the cache."""
    if clear:
        with message_fence("Clearing cache..."):
            if cache_names := ", ".join(project.clear_cache(patterns)):
                click.echo(f"Cache cleared successfully: {cache_names}.\n")
            else:
                click.echo(
                    "No matching results.\n"
                    if patterns
                    else "The cache is already cleared.\n"
                )
    else:
        with message_fence("Inspecting cache..."):
            click.echo(
                "\n".join(project.inspect_cache(patterns))
                or (
                    "No matching results.\n"
                    if patterns
                    else "The cache is completely clear.\n"
                )
            )


@command
@click.argument("target", required=False)
@click.option(
    "-c",
    "--clear",
    is_flag=True,
    help="Clear the link.",
)
def link(project: Project, target: Optional[str], clear: bool):
    """Link the generated resource pack and data pack to Minecraft."""
    if clear:
        with message_fence("Clearing project link..."):
            project.clear_link()
    else:
        with message_fence("Linking project..."):
            click.echo("\n".join(project.link(target)))


def main():
    """Invoke the command-line entrypoint."""
    beet(prog_name="beet")
