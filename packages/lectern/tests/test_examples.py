from glob import glob
from typing import Any

import pytest
from beet import run_beet

from lectern import Document

EXAMPLES_LINKS = sorted(glob("examples/with_links/*.md")) + ["README.md"]
EXAMPLES = sorted(glob("examples/*.txt")) + sorted(glob("examples/*.md")) + EXAMPLES_LINKS


@pytest.mark.parametrize("path", EXAMPLES)
def test_text(snapshot: Any, path: str):
    assert snapshot("pack.txt") == Document(path=path)


@pytest.mark.parametrize("path", EXAMPLES)
def test_text_equality(snapshot: Any, path: str):
    document = Document(path=path)
    assert document == Document(text=document.get_text())


@pytest.mark.parametrize("path", EXAMPLES)
def test_markdown(snapshot: Any, path: str):
    assert snapshot("pack.md") == Document(path=path)


@pytest.mark.parametrize("path", EXAMPLES)
def test_markdown_equality(snapshot: Any, path: str):
    document = Document(path=path)
    assert document == Document(markdown=document.get_markdown())


@pytest.mark.parametrize("path", EXAMPLES_LINKS)
def test_markdown_external_files(snapshot: Any, path: str):
    assert snapshot("pack.md_external_files") == Document(path=path)


def test_beet_project(snapshot: Any):
    with run_beet(directory="examples/with_beet") as ctx:
        ctx.data.name = None
        ctx.assets.name = None
        assert snapshot("pack.md") == ctx.inject(Document)
