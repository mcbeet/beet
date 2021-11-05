import pytest

from lectern import DirectiveRegistry, Fragment, TextExtractor


@pytest.mark.parametrize(
    "source,  fragment",
    [
        (
            "@function demo:foo\nsay foo\n",
            Fragment(0, 3, "function", None, ["demo:foo"], "say foo\n"),
        ),
        (
            "@function() demo:foo\nsay foo\n",
            Fragment(0, 3, "function", "", ["demo:foo"], "say foo\n"),
        ),
        (
            "@function(strip_final_newline) demo:foo\nsay foo\n",
            Fragment(
                0, 3, "function", "strip_final_newline", ["demo:foo"], "say foo\n"
            ),
        ),
    ],
)
def test_parse(source: str, fragment: Fragment):
    parsed_fragment = next(
        TextExtractor().parse_fragments(source, DirectiveRegistry().resolve())
    )
    assert fragment == parsed_fragment
