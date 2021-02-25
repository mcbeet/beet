import pytest

from lectern import TextExtractor
from lectern.directive import Fragment, get_builtin_directives


@pytest.mark.parametrize(
    "source,  fragment",
    [
        (
            "@function demo:foo\nsay foo\n",
            Fragment("function", None, ["demo:foo"], "say foo\n"),
        ),
        (
            "@function() demo:foo\nsay foo\n",
            Fragment("function", "", ["demo:foo"], "say foo\n"),
        ),
        (
            "@function(strip_final_newline) demo:foo\nsay foo\n",
            Fragment("function", "strip_final_newline", ["demo:foo"], "say foo\n"),
        ),
    ],
)
def test_parse(source: str, fragment: Fragment):
    parsed_fragment = next(
        TextExtractor().parse_fragments(source, get_builtin_directives())
    )
    assert fragment == parsed_fragment
