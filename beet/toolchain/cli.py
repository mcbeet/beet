__all__ = [
    "MainGroup",
    "BeetHelpColorsMixin",
    "BeetCommand",
    "BeetGroup",
    "LogHandler",
    "main",
    "beet",
    "format_error",
    "error_handler",
    "message_fence",
]


import logging
from contextlib import contextmanager
from importlib.metadata import entry_points
from typing import Any, Callable, Iterator, Optional

import click
from click_help_colors import HelpColorsCommand, HelpColorsGroup

from beet import __version__
from beet.core.error import BeetException, WrappedException
from beet.core.utils import format_exc

from .project import Project


def format_error(
    message: str,
    exception: Optional[BaseException] = None,
    padding: int = 0,
) -> str:
    """Format a given error message and exception."""
    output = "\n" * padding
    output += click.style("Error: " + message, fg="red", bold=True) + "\n"
    if exception:
        output += "\n" + format_exc(exception)
    output += "\n" * padding
    return output


@contextmanager
def error_handler(should_exit: bool = False, format_padding: int = 0) -> Iterator[None]:
    """Context manager that catches and displays exceptions."""
    exception = None

    try:
        yield
    except WrappedException as exc:
        message = str(exc)
        if not exc.hide_wrapped_exception:
            exception = exc.__cause__
    except BeetException as exc:
        message = str(exc)
    except (click.Abort, KeyboardInterrupt):
        click.echo()
        message = "Aborted."
    except (click.ClickException, click.exceptions.Exit):
        raise
    except Exception as exc:
        message = "An unhandled exception occurred. This could be a bug."
        exception = exc
    else:
        return

    if LogHandler.has_output and not format_padding:
        click.echo()

    click.echo(format_error(message, exception, format_padding), nl=False)

    if should_exit:
        raise click.exceptions.Exit(1)


@contextmanager
def message_fence(message: str) -> Iterator[None]:
    """Context manager used to report the begining and the end of a cli operation."""
    click.secho(message + "\n", fg="red")
    yield
    if LogHandler.has_output:
        click.echo()
    click.secho("Done!", fg="green", bold=True)
    LogHandler.has_output = False


class LogHandler(logging.Handler):
    """Logging handler for the beet cli."""

    style: Any = {
        "CRITICAL": {"fg": "red", "bold": True},
        "ERROR": {"fg": "red", "bold": True},
        "WARNING": {"fg": "yellow", "bold": True},
        "INFO": {},
        "DEBUG": {"fg": "magenta"},
    }

    abbreviations: Any = {
        "CRITICAL": "CRIT",
        "WARNING": "WARN",
    }

    has_output: bool = False

    def __init__(self):
        super().__init__()
        self.setFormatter(logging.Formatter("%(message)s"))

    def emit(self, record: logging.LogRecord):
        LogHandler.has_output = True
        level = self.abbreviations.get(record.levelname, record.levelname)
        style = self.style[record.levelname]

        line_prefix = click.style(f"       |", **style)

        leading_line, *lines = self.format(record).splitlines()
        if record.levelname in ["ERROR", "CRITICAL"]:
            leading_line = click.style(leading_line, **style)

        leading_line = (
            click.style(getattr(record, "prefix", record.name), bold=True, fg="black")
            + "  "
            + leading_line
        )

        click.echo(click.style(f"{level:<7}|", **style) + " " + leading_line)

        if annotate := getattr(record, "annotate", None):
            lines.insert(0, click.style(str(annotate), fg="cyan"))

        for line in lines:
            click.echo(line_prefix + " " * bool(line) + line)


class BeetHelpColorsMixin:
    """Mixin that fixes usage formatting."""

    help_headers_color: str
    help_options_color: str

    def __init__(self, *args: Any, **kwargs: Any):
        kwargs.setdefault("help_headers_color", "red")
        kwargs.setdefault("help_options_color", "green")
        super().__init__(*args, **kwargs)

    def format_usage(self, ctx: click.Context, formatter: Any):
        formatter.write_usage(
            ctx.command_path,
            " ".join(self.collect_usage_pieces(ctx)),  # type: ignore
            click.style("Usage", fg=self.help_headers_color) + ": ",
        )


class BeetCommand(BeetHelpColorsMixin, HelpColorsCommand):
    """Click command subclass for the beet command-line."""


class BeetGroup(BeetHelpColorsMixin, HelpColorsGroup):
    """Click group subclass for the beet command-line."""

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

    def add_command(self, cmd: click.Command, name: Optional[str] = None) -> None:
        if cmd.callback:  # type: ignore
            cmd.callback = error_handler(should_exit=True)(cmd.callback)  # type: ignore
        return super().add_command(cmd, name=name)

    def command(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Callable[[Callable[..., Any]], click.Command]:
        kwargs.setdefault("cls", BeetCommand)
        return super().command(*args, **kwargs)

    def group(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Callable[[Callable[..., Any]], click.Group]:
        kwargs.setdefault("cls", BeetGroup)
        return super().group(*args, **kwargs)


class MainGroup(BeetGroup):
    """The root group of the beet command-line."""

    def __init__(self, *args: Any, **kwargs: Any):
        kwargs.setdefault("invoke_without_command", True)
        kwargs.setdefault("context_settings", {"help_option_names": ("-h", "--help")})
        super().__init__(*args, **kwargs)
        self.entry_points_loaded = False

    def load_entry_points(self):
        """Load commands from installed entry points if they haven't been loaded yet."""
        if self.entry_points_loaded:
            return

        self.entry_points_loaded = True

        for ep in entry_points(group="beet", name="commands"):
            ep.load()

    def get_command(self, ctx: click.Context, cmd_name: str) -> Optional[click.Command]:
        self.load_entry_points()
        return super().get_command(ctx, cmd_name)

    def list_commands(self, ctx: click.Context) -> list[str]:
        self.load_entry_points()
        return super().list_commands(ctx)


@click.group(cls=MainGroup)  # type: ignore
@click.pass_context
@click.option(
    "-p",
    "--project",
    metavar="PATH",
    help="Select project.",
)
@click.option(
    "-s",
    "--set",
    metavar="OPTION",
    multiple=True,
    help="Set config option.",
)
@click.option(
    "-l",
    "--log",
    metavar="LEVEL",
    type=click.Choice(
        ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"], case_sensitive=False
    ),
    default="WARNING",
    help="Configure output verbosity.",
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
    project: Optional[str],
    set: list[str],
    log: str,
):
    """The beet toolchain."""
    logger = logging.getLogger()
    logger.setLevel(log)
    logger.addHandler(LogHandler())

    project_obj = ctx.ensure_object(Project)

    if set:
        project_obj.config_overrides = set
    if project:
        project_obj.config_path = project

    if not ctx.invoked_subcommand:
        if build := beet.get_command(ctx, "build"):
            ctx.invoke(build)


def main():
    """Invoke the beet command-line."""
    beet(prog_name="beet")
