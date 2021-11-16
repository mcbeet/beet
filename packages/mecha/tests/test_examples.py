import os

import pytest
from beet import run_beet
from lectern import Document
from pytest_insta import SnapshotFixture


@pytest.mark.parametrize("directory", os.listdir("examples"))
def test_build(snapshot: SnapshotFixture, directory: str):
    with run_beet(directory=f"examples/{directory}") as ctx:
        assert snapshot("pack.md") == ctx.inject(Document)
