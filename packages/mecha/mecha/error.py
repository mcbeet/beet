__all__ = [
    "MechaError",
    "InvalidEscapeSequence",
    "UnrecognizedParser",
]


class MechaError(Exception):
    """Base class for all mecha errors."""


class InvalidEscapeSequence(MechaError):
    """Raised when a QuotedStringHandler encounters an invalid escape sequence."""

    characters: str
    index: int

    def __init__(self, characters: str, index: int):
        super().__init__(characters, index)
        self.characters = characters
        self.index = index


class UnrecognizedParser(MechaError):
    """Raised when delegating to an unrecognized parser."""

    parser: str

    def __init__(self, parser: str):
        super().__init__(parser)
        self.parser = parser
