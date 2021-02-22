import pytest

from lectern import TextExtractor
from lectern.directive import Fragment, get_builtin_directives


@pytest.mark.parametrize(
    "source, directive, fragment",
    [
        (
            "@function demo:foo\nsay foo\n",
            "function",
            Fragment(None, ["demo:foo"], "say foo\n"),
        ),
        (
            "@function() demo:foo\nsay foo\n",
            "function",
            Fragment("", ["demo:foo"], "say foo\n"),
        ),
        (
            "@function(strip_final_newline) demo:foo\nsay foo\n",
            "function",
            Fragment("strip_final_newline", ["demo:foo"], "say foo\n"),
        ),
    ],
)
def test_parse(source: str, directive: str, fragment: Fragment):
    parsed_directive, parsed_fragment = next(
        TextExtractor().parse_fragments(source, get_builtin_directives())
    )
    assert directive == parsed_directive
    assert fragment == parsed_fragment
