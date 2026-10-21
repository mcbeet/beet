__all__ = [
    "CommandArgument",
    "CommandPrototype",
    "CommandSignature",
]


from typing import NamedTuple

type CommandSignature = tuple[str | CommandArgument, ...]


class CommandArgument(NamedTuple):
    """Class representing an argument in a command prototype."""

    name: str
    scope: tuple[str, ...]


class CommandPrototype(NamedTuple):
    """Class representing a command prototype."""

    identifier: str
    signature: CommandSignature
    arguments: tuple[int, ...]

    def get_argument(self, arg: str | int) -> CommandArgument:
        """Return the argument corresponding to the given name or index."""
        if isinstance(arg, str):
            for i in range(len(self.arguments)):
                argument = self.get_argument(i)
                if argument.name == arg:
                    return argument
            raise ValueError(f"No argument {arg!r}.")

        return self.signature[self.arguments[arg]]  # pyright: ignore[reportReturnType]

    def usage(self) -> str:
        """Return a string showing the command usage."""
        return " ".join(
            arg if isinstance(arg, str) else f"<{arg.name}>" for arg in self.signature
        )
