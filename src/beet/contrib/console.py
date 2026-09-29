"""Singleton for managing the interactive console."""

__all__ = [
    "Console",
    "start",
    "stop",
    "ConsoleSubmit",
    "ConsoleInterrupt",
    "ConsoleStop",
]


from collections.abc import Callable
import logging
from pathlib import Path
from threading import Condition, Thread
from typing import Self
import _thread

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import (
    AutoSuggest,
    AutoSuggestFromHistory,
    DynamicAutoSuggest,
)
from prompt_toolkit.completion import Completer, DummyCompleter, DynamicCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.styles import Style
from prompt_toolkit.validation import DummyValidator, DynamicValidator, Validator

from beet import Context
from beet.contrib.singleton import singleton


def beet_default(ctx: Context):
    ctx.require(start)


def start(ctx: Context):
    """Plugin to start the console."""
    cache = ctx.cache["console"]

    console = ctx.inject(singleton(Console))
    console.start(cache.directory / "history")


def stop(ctx: Context):
    """Plugin to stop the console."""
    console = ctx.inject(singleton(Console))
    console.stop()


type ConsoleSubmit = Callable[[str], None]
type ConsoleInterrupt = Callable[[], None]


class ConsoleStop(Exception):
    """Raised to stop the console."""


class Console:
    cond: Condition
    session: PromptSession[str] | None
    submit: ConsoleSubmit
    interrupt: ConsoleInterrupt
    completer: Completer
    validator: Validator
    auto_suggest: AutoSuggest
    style: Style

    def __init__(self):
        self.cond = Condition()
        self.session = None
        self.submit = lambda _: None
        self.interrupt = _thread.interrupt_main
        self.completer = DummyCompleter()
        self.validator = DummyValidator()
        self.auto_suggest = AutoSuggestFromHistory()
        self.style = Style(
            [
                ("prompt", "fg:ansibrightcyan"),
                ("validation-toolbar", "fg:ansibrightyellow bg:ansiblack"),
            ]
        )

    def start(self, history: Path):
        with self.cond:
            if self.session:
                return

            self.session = PromptSession(
                message="\n>>>>>>>> ",
                style=self.style,
                history=FileHistory(history),
                auto_suggest=DynamicAutoSuggest(lambda: self.auto_suggest),
                enable_history_search=True,
                completer=DynamicCompleter(lambda: self.completer),
                validator=DynamicValidator(lambda: self.validator),
                validate_while_typing=False,
            )

            Thread(target=self._daemon, args=(self.session,), daemon=True).start()

    def stop(self):
        with self.cond:
            if self.session:
                self.session.app.exit(exception=ConsoleStop)
            self.cond.wait_for(lambda: self.session is None)

    def _daemon(self, session: PromptSession):
        logging.getLogger("asyncio").addFilter(_filter_asyncio_logs)

        with patch_stdout():
            while True:
                try:
                    command = session.prompt()
                except KeyboardInterrupt:
                    if session.default_buffer.text:
                        continue
                    with self.cond:
                        self.interrupt()
                    break
                except EOFError:
                    with self.cond:
                        self.interrupt()
                    break
                except ConsoleStop:
                    break

                with self.cond:
                    self.submit(command)

        with self.cond:
            self.session = None
            self.cond.notify_all()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_):
        self.stop()


def _filter_asyncio_logs(record: logging.LogRecord) -> bool:
    return not record.getMessage().startswith("Using proactor:")
