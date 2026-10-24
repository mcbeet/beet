"""Plugin to provide playground interactivity."""

__all__ = [
    "setup_console",
]


from functools import partial
from threading import Thread

from prompt_toolkit.buffer import ValidationState
from prompt_toolkit.document import Document
from prompt_toolkit.validation import ValidationError, Validator

from beet import Context
from beet.contrib.autosave import Autosave
from beet.contrib.console import Console, ConsoleInterrupt
from beet.contrib.playground import Playground
from beet.contrib.singleton import singleton


def beet_default(ctx: Context):
    ctx.require("beet.contrib.playground.clean")

    autosave = ctx.inject(Autosave)
    if autosave.link:
        # Use add_link instead of add_output to let LinkManager.autosave_handler take priority
        autosave.add_link("beet.contrib.playground.link")
        autosave.add_link("beet.contrib.playground.reload")
    else:
        autosave.add_output("beet.contrib.playground.link")
        autosave.add_output("beet.contrib.playground.reload")

    ctx.require(singleton(setup_console))
    ctx.require("beet.contrib.playground")
    ctx.require("beet.contrib.console")


def setup_console(console: Console, playground: Playground):
    with console.cond:
        console.submit = playground.run
        console.interrupt = partial(_interrupt, playground, console.interrupt)
        console.validator = PlaygroundValidator(playground, console.validator)

    Thread(target=_revalidate, args=(console, playground), daemon=True).start()


def _interrupt(playground: Playground, next: ConsoleInterrupt):
    playground.stop()
    next()


class PlaygroundValidator(Validator):
    playground: Playground
    next: Validator

    def __init__(self, playground: Playground, next: Validator):
        self.playground = playground
        self.next = next

    def validate(self, document: Document):
        with self.playground.cond:
            if not self.playground.ready:
                raise ValidationError(
                    message="Playground not ready!",
                    cursor_position=len(document.text),
                )
        self.next.validate(document)


def _revalidate(console: Console, playground: Playground):
    while True:
        with playground.cond:
            playground.cond.wait_for(lambda: playground.ready)
            with console.cond:
                if console.session:
                    buffer = console.session.default_buffer
                    if buffer.validation_state != ValidationState.UNKNOWN:
                        buffer.validation_state = ValidationState.UNKNOWN
                        buffer.validate()
            playground.cond.wait_for(lambda: not playground.ready)
