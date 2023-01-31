"""Run deferred callbacks."""


__all__ = [
    "Defer",
    "DeferHandler",
    "AstDefer",
    "AstDeferCommand",
    "defer",
]


from dataclasses import dataclass
from typing import Any, Callable, Generator, List, TypeVar

from beet import Context
from beet.core.utils import required_field
from mecha import (
    AstChildren,
    AstCommandSentinel,
    AstNode,
    AstRoot,
    Dispatcher,
    Mecha,
    MutatingReducer,
    rule,
)

from bolt import Runtime

CallbackType = TypeVar("CallbackType", bound=Callable[[], Any])


def beet_default(ctx: Context):
    ctx.require(defer)


def defer(ctx: Context):
    """Plugin that makes the defer utility available globally."""
    runtime = ctx.inject(Runtime)
    defer = ctx.inject(Defer)
    runtime.expose("defer", defer)


@dataclass(frozen=True, slots=True)
class AstDefer(AstNode):
    """Ast defer node."""

    callback: Callable[[], Any] = required_field()


@dataclass(frozen=True, slots=True)
class AstDeferCommand(AstCommandSentinel):
    """Ast defer command node.

    Same as AstDefer but allows the node to pass as a regular AstCommand.
    """

    callback: Callable[[], Any] = required_field()


@dataclass
class DeferHandler(MutatingReducer):
    runtime: Runtime = required_field()

    @rule(AstDefer)
    @rule(AstDeferCommand)
    def defer(self, node: AstDefer | AstDeferCommand) -> Generator[AstNode, Any, Any]:
        with self.runtime.modules.error_handler(
            "Deferred callback raised an exception."
        ):
            result = node.callback()

        if isinstance(result, AstNode):
            result = yield result
        elif isinstance(result, AstChildren):
            children: List[Any] = []
            for child in result:  # type: ignore
                deferred_child = yield child
                children.append(deferred_child)
            result = AstChildren(children)

        return result


class Defer:
    runtime: Runtime
    handler: Dispatcher[AstRoot]

    def __init__(self, ctx: Context):
        self.runtime = ctx.inject(Runtime)
        self.handler = DeferHandler(runtime=self.runtime)
        mc = ctx.inject(Mecha)
        mc.steps.insert(mc.steps.index(self.runtime.evaluate) + 1, self.handler)

    def __call__(self, callback: CallbackType) -> CallbackType:
        self.runtime.commands.append(
            AstDeferCommand(
                callback=lambda: AstChildren(self.runtime.capture_output(callback))
            )
        )
        return callback
