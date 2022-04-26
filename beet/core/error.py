__all__ = [
    "BeetException",
    "BubbleException",
    "WrappedException",
]


class BeetException(Exception):
    """Base class for beet exceptions."""


class BubbleException(BeetException):
    """Exceptions inheriting from this class will bubble up through exception wrappers."""


class WrappedException(BubbleException):
    """Raised to wrap an underlying exception."""

    __cause__: Exception
    hide_wrapped_exception: bool

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.hide_wrapped_exception = False
