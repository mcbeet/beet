from glob import glob
from typing import Any

import pytest

from lectern import Document

EXAMPLES = [
    *glob("examples/*.txt"),
    *glob("examples/*.md"),
    "README.md",
]


@pytest.mark.parametrize("path", EXAMPLES)
def test_text(snapshot: Any, path: str):
    assert snapshot("pack.txt") == Document(path=path)


@pytest.mark.parametrize("path", EXAMPLES)
def test_markdown(snapshot: Any, path: str):
    assert snapshot("pack.md") == Document(path=path)
