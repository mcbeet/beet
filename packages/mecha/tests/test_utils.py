# AI-assisted (Claude, Anthropic): see the commit message.
from tokenstream import SourceLocation

from mecha.utils import underline_code


def loc(pos: int, lineno: int, colno: int) -> SourceLocation:
    return SourceLocation(pos, lineno, colno)


def lines(text: str) -> list[str]:
    return [line.rstrip() for line in text.splitlines()]


def test_underline_token():
    source = "say ok\nfoo bar\nsay z\n"
    result = underline_code(source, loc(7, 2, 1), loc(10, 2, 4))
    assert lines(result) == [
        "     1 |  say ok",
        "     2 |  foo bar",
        "       :  ^^^",
        "     3 |  say z",
    ]


def test_underline_newline_token_points_at_end_of_line():
    # The newline token ends at column 1 of the next line. The caret must be
    # drawn on the line that is missing something, not under the next line.
    source = "say a\nexecute as @a run\nsay b\n"
    result = underline_code(source, loc(23, 2, 18), loc(24, 3, 1))
    assert lines(result) == [
        "     1 |  say a",
        "     2 |  execute as @a run",
        "       :                   ^",
        "     3 |  say b",
    ]


def test_underline_newline_token_at_end_of_file():
    source = "execute as @a run\n"
    result = underline_code(source, loc(17, 1, 18), loc(18, 2, 1))
    assert lines(result) == [
        "     1 |  execute as @a run",
        "       :                   ^",
    ]


def test_underline_eof_token_without_trailing_newline():
    source = "say a\nexecute as @a run"
    result = underline_code(source, loc(23, 2, 18), loc(23, 2, 18))
    assert lines(result) == [
        "     1 |  say a",
        "     2 |  execute as @a run",
        "       :                   ^",
    ]


def test_underline_multiline_span_still_covers_both_lines():
    source = "say a\nsay bc\nsay d\n"
    result = underline_code(source, loc(4, 1, 5), loc(10, 2, 4))
    assert lines(result) == [
        "     1 |  say a",
        "       :      ^",
        "     2 |  say bc",
        "       :  ^^^",
        "     3 |  say d",
    ]
