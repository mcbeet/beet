__all__ = [
    "CommandEmitter",
]


from contextlib import contextmanager
from typing import Any, Callable, Generator, Iterator, List, Optional, ParamSpec

from mecha import AstCommand, AstNode, AstRoot

from .utils import internal

P = ParamSpec("P")


class CommandEmitter:
    """Command emitter."""

    commands: List[AstCommand]

    def __init__(self):
        self.commands = []

    @contextmanager
    def scope(
        self,
        commands: Optional[List[AstCommand]] = None,
    ) -> Iterator[List[AstCommand]]:
        """Create a new scope to gather commands."""
        if commands is None:
            commands = []

        previous_commands = self.commands
        self.commands = commands

        try:
            yield commands
        finally:
            self.commands = previous_commands

    @internal
    def capture_output(
        self,
        f: Callable[P, Any],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> List[AstCommand]:
        """Invoke a user-defined function and return the list of generated commands."""
        with self.scope() as output:
            result = f(*args, **kwargs)

            if isinstance(result, Generator):
                try:
                    while True:
                        node: Any = next(result)  # type: ignore
                        if isinstance(node, AstRoot):
                            self.commands.extend(node.commands)
                        elif isinstance(node, AstCommand):
                            self.commands.append(node)
                        elif node:
                            msg = f"Invalid command of type {type(node)!r}."
                            raise TypeError(msg)
                except StopIteration as exc:
                    result = exc.value

        if not result:
            result = []
        elif isinstance(result, AstNode):
            result = [result]

        for node in result:
            if isinstance(node, AstRoot):
                output.extend(node.commands)
            elif isinstance(node, AstCommand):
                output.append(node)
            elif node:
                msg = f"Invalid command of type {type(node)!r}."
                raise TypeError(msg)

        return output
