import os
from pathlib import Path

import pytest
from beet import ProjectCache, run_beet
from lectern import Document
from pytest_insta import SnapshotFixture


@pytest.mark.parametrize("directory", os.listdir("examples"))
def test_build(snapshot: SnapshotFixture, directory: str, tmp_path: Path):
    with run_beet(
        directory=f"examples/{directory}",
        cache=ProjectCache(tmp_path / ".beet_cache", tmp_path / "generated"),
    ) as ctx:
        assert snapshot("pack.md") == ctx.inject(Document)
