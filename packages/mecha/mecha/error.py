__all__ = [
    "MechaError",
    "InvalidEscapeSequence",
]


class MechaError(Exception):
    """Base class for all mecha errors."""


class InvalidEscapeSequence(MechaError):
    """Raised when a QuotedStringHandler encounters an invalid escape sequence."""

    characters: str
    index: int

    def __init__(self, characters: str, index: int):
        self.characters = characters
        self.index = index
