from pathlib import Path

import pytest
from pytest_insta import SnapshotFixture
from tokenstream import TokenStream

from mecha.contrib.validation import parse_mcdoc

MCDOC_EXAMPLES = Path("tests/resources/mcdoc_examples.txt").read_text().split("###\n")


@pytest.mark.parametrize(
    "source",
    MCDOC_EXAMPLES,
    ids=range(len(MCDOC_EXAMPLES)),
)
def test_parse(snapshot: SnapshotFixture, source: str):
    mcdoc = parse_mcdoc(TokenStream(source))
    assert snapshot() == f"{source}---\n{mcdoc.dump()}\n"
