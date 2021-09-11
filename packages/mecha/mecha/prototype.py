__all__ = [
    "CommandSignature",
    "CommandPrototype",
    "CommandArgument",
]


from typing import NamedTuple, Tuple, Union

CommandSignature = Tuple[Union[str, "CommandArgument"], ...]


class CommandArgument(NamedTuple):
    """Class representing an argument in a command prototype."""

    name: str
    scope: Tuple[str, ...]


class CommandPrototype(NamedTuple):
    """Class representing a command prototype."""

    identifier: str
    signature: CommandSignature
    arguments: Tuple[int, ...]

    def get_argument(self, arg: Union[str, int]) -> CommandArgument:
        """Return the argument corresponding to the given name or index."""
        if isinstance(arg, str):
            for i in self.arguments:
                if self.get_argument(i).name == arg:
                    arg = i
                    break
            else:
                arg = len(self.signature)

        return self.signature[self.arguments[arg]]  # type: ignore
