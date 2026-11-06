import os

import pytest
from pytest_insta import SnapshotFixture

from beet import run_beet

from lectern import Document


@pytest.mark.parametrize("directory", sorted(os.listdir("examples")))
def test_build(snapshot: SnapshotFixture, directory: str):
    with run_beet(directory=f"examples/{directory}") as ctx:
        assert snapshot("pack.md") == ctx.inject(Document)
