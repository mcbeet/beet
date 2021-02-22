__all__ = [
    "Fragment",
    "InvalidFragment",
]


from dataclasses import dataclass
from typing import List, Optional, Tuple, Union, overload

from beet import FormattedPipelineException


class InvalidFragment(FormattedPipelineException):
    """Raised when a fragment can not be processed."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


@dataclass(frozen=True)
class Fragment:
    """Class representing a fragment annotated by a directive."""

    modifier: Optional[str]
    arguments: List[str]
    content: Union[str, bytes]

    @overload
    def expect(self):
        ...

    @overload
    def expect(self, name1: str) -> str:
        ...

    @overload
    def expect(self, name1: str, name2: str, *names: str) -> Tuple[str, ...]:
        ...

    def expect(self, *names: str):
        """Check directive arguments."""
        if missing := names[len(self.arguments) :]:
            msg = f"Missing directive argument {', '.join(map(repr, missing))}."
            raise InvalidFragment(msg)
        if extra := self.arguments[len(names) :]:
            msg = f"Unexpected directive argument {', '.join(map(repr, extra))}."
            raise InvalidFragment(msg)
        if len(self.arguments) == 0:
            return
        if len(self.arguments) == 1:
            return self.arguments[0]
        return self.arguments

    def apply_modifier(self) -> Union[str, bytes]:
        if self.modifier == "strip_final_newline" and self.content[-1:] == "\n":
            return self.content[:-1]
        return self.content
