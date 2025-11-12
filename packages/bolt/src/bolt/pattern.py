__all__ = [
    "KEYWORD_PATTERN",
    "TRUE_PATTERN",
    "FALSE_PATTERN",
    "NULL_PATTERN",
    "IDENTIFIER_PATTERN",
    "DOCSTRING_PATTERN",
    "MODULE_PATTERN",
    "STRING_PATTERN",
    "NUMBER_PATTERN",
    "RESOURCE_LOCATION_PATTERN",
]


import keyword

KEYWORD_PATTERN: str = "|".join(rf"\b{kw}\b" for kw in keyword.kwlist)

TRUE_PATTERN: str = r"\b[tT]rue\b"
FALSE_PATTERN: str = r"\b[fF]alse\b"
NULL_PATTERN: str = r"\b(?:null|None)\b"
IDENTIFIER_PATTERN: str = rf"(?!_bolt_|{KEYWORD_PATTERN})[a-zA-Z_][a-zA-Z0-9_]*\b"
MODULE_PATTERN: str = rf"{IDENTIFIER_PATTERN}(?:\.{IDENTIFIER_PATTERN})*"
DOCSTRING_PATTERN: str = r'r?"""(?:\\.|[^\\])*?"""' "|" r"r?'''(?:\\.|[^\\])*?'''"
STRING_PATTERN: str = r'r?"(?:\\.|[^\\\n])*?"' "|" r"r?'(?:\\.|[^\\\n])*?'"
NUMBER_PATTERN: str = r"(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?\b"
RESOURCE_LOCATION_PATTERN: str = r"(?:\.\./|\./|[0-9a-z_\-\.]+:)[0-9a-z_./-]+"
