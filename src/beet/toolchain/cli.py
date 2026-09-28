__all__ = [
    "MainGroup",
    "BeetHelpColorsMixin",
    "BeetCommand",
    "BeetGroup",
    "LogHandler",
    "main",
    "beet",
    "error_handler",
    "message_fence",
]


import logging
from contextlib import contextmanager
from importlib.metadata import entry_points
from typing import Any, Callable, Iterator, List, Optional

import click
from click_help_colors import HelpColorsCommand, HelpColorsGroup
from prompt_toolkit import print_formatted_text as print
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.styles import Style

from beet import __version__
from beet.core.error import BeetException, WrappedException
from beet.core.utils import format_exc

from .project import Project


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
        print()
        message = "Aborted."
    except (click.ClickException, click.exceptions.Exit):
        raise
    except Exception as exc:
        message = "An unhandled exception occurred. This could be a bug."
        exception = exc
    else:
        return

    if LogHandler.has_output and not format_padding:
        print()

    message = [
        ("", "\n" * format_padding),
        ("fg:ansibrightred", f"Error: {message}"),
        ("", "\n"),
        ("", "\n" + format_exc(exception) if exception else ""),
        ("", "\n" * format_padding),
    ]
    print(FormattedText(message), end="")

    if should_exit:
        raise click.exceptions.Exit(1)


@contextmanager
def message_fence(message: str) -> Iterator[None]:
    """Context manager used to report the beginning and the end of a cli operation."""
    print(FormattedText([("fg:ansired", message + "\n")]))
    yield
    if LogHandler.has_output:
        print()
    print(FormattedText([("fg:ansibrightgreen", "Done!")]))
    LogHandler.has_output = False


class LogHandler(logging.Handler):
    """Logging handler for the beet cli."""

    style = Style(
        [
            ("level critical", "fg:ansibrightred"),
            ("level error", "fg:ansibrightred"),
            ("level warning", "fg:ansibrightyellow"),
            ("level info", ""),
            ("level debug", "fg:ansimagenta"),
            ("leading_line critical", "fg:ansibrightred"),
            ("leading_line error", "fg:ansibrightred"),
            ("prefix", "fg:ansibrightblack"),
            ("annotate", "fg:ansicyan"),
        ]
    )

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
        message = []
        level_class = f"class:{record.levelname.lower()}"

        lines = self.format(record).splitlines()
        if leading_line := not getattr(record, "continue", False) and lines.pop(0):
            level = self.abbreviations.get(record.levelname, record.levelname)
            message += [(f"class:level {level_class}", f"{level:<7}|"), ("", " ")]

            if prefix := getattr(record, "prefix", record.name):
                message += [("class:prefix", prefix), ("", "  ")]

            message += [(f"class:leading_line {level_class}", leading_line), ("", "\n")]

        if annotate := getattr(record, "annotate", None):
            message += [
                (f"class:level {level_class}", "       |"),
                ("", " "),
                ("class:annotate", str(annotate)),
                ("", "\n"),
            ]

        for line in lines:
            message += [(f"class:level {level_class}", "       |")]
            if line:
                message += [("", " "), ("", line)]
            message += [("", "\n")]

        print(FormattedText(message), style=self.style, end="")


class BeetHelpColorsMixin:
    """Mixin that fixes usage formatting."""

    help_headers_color: str = "red"
    help_options_color: str = "green"

    def __init__(self, *args: Any, **kwargs: Any):
        kwargs.setdefault("help_headers_color", self.help_headers_color)
        kwargs.setdefault("help_options_color", self.help_options_color)
        super().__init__(*args, **kwargs)

    def format_usage(self, ctx: click.Context, formatter: Any):
        formatter.write_usage(
            ctx.command_path,
            " ".join(self.collect_usage_pieces(ctx)),  # pyright: ignore[reportAttributeAccessIssue]
            click.style("Usage", fg=self.help_headers_color),
        )


class BeetCommand(BeetHelpColorsMixin, HelpColorsCommand):  # pyright: ignore[reportUnsafeMultipleInheritance]
    """Click command subclass for the beet command-line."""


class BeetGroup(BeetHelpColorsMixin, HelpColorsGroup):  # pyright: ignore[reportUnsafeMultipleInheritance]
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
        if cmd.callback:
            cmd.callback = error_handler(should_exit=True)(cmd.callback)
        return super().add_command(cmd, name=name)

    def command(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Callable[[Callable[..., Any]], click.Command]:
        kwargs.setdefault("cls", BeetCommand)
        return super().command(*args, **kwargs)

    def group(  # pyright: ignore[reportIncompatibleMethodOverride]
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

    def list_commands(self, ctx: click.Context) -> List[str]:
        self.load_entry_points()
        return super().list_commands(ctx)


@click.group(cls=MainGroup)
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
    default="INFO",
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
    set: List[str],
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
        if build := beet.get_command(ctx, "build"):  # pyright: ignore[reportFunctionMemberAccess]
            ctx.invoke(build)


def main():
    """Invoke the beet command-line."""
    beet(prog_name="beet")
