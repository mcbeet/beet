from enum import StrEnum, auto

class Color(StrEnum):
    RED = 'r'
    GREEN = 'g'
    BLUE = 'b'
    UNKNOWN = auto()

say (Color.RED, Color.GREEN, Color.BLUE, Color.UNKNOWN)
