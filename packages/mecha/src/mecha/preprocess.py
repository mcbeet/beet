__all__ = [
    "wrap_backslash_continuation",
    "BACKSLASH_CONTINUATION_REGEX",
]


import re
from itertools import islice

from tokenstream import INITIAL_LOCATION, SourceLocation

BACKSLASH_CONTINUATION_REGEX = re.compile(r"(\\[ \t]*\r?\n[ \t]*)")


def wrap_backslash_continuation(
    source: str,
) -> tuple[str, list[SourceLocation], list[SourceLocation]]:
    it = iter(BACKSLASH_CONTINUATION_REGEX.split(source))
    text = next(it)

    result = [text]
    source_mappings: list[SourceLocation] = []
    preprocessed_mappings: list[SourceLocation] = []

    source_location = INITIAL_LOCATION.skip_over(text)
    preprocessed_location = source_location

    while True:
        try:
            backslash, text = islice(it, 2)
        except ValueError:
            break

        source_location = source_location.skip_over(backslash)
        source_mappings.append(source_location)
        preprocessed_mappings.append(preprocessed_location)

        result.append(text)
        source_location = source_location.skip_over(text)
        preprocessed_location = preprocessed_location.skip_over(text)

    return "".join(result), source_mappings, preprocessed_mappings
