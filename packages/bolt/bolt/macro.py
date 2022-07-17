__all__ = [
    "invoke_macro",
]


from typing import Any, Generator, Iterable

from mecha import AstCommand, AstNode, AstRoot

from .utils import internal


@internal
def invoke_macro(
    runtime: Any,
    function: Any,
    identifier: str,
    arguments: Iterable[Any],
):
    """Invoke a user-defined macro and return the list of generated commands."""
    with runtime.scope() as output:
        result = function(*arguments)

        if isinstance(result, Generator):
            try:
                while True:
                    node: Any = next(result)  # type: ignore
                    if isinstance(node, AstRoot):
                        runtime.commands.extend(node.commands)
                    elif isinstance(node, AstCommand):
                        runtime.commands.append(node)
                    elif node:
                        msg = f'Emit invalid command of type {type(node)!r} from macro "{identifier}".'
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
            msg = f'Return invalid command of type {type(node)!r} from macro "{identifier}".'
            raise TypeError(msg)

    return output
