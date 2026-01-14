import os

import pytest
from pytest_insta import SnapshotFixture

from beet import run_beet

EXAMPLES = [f for f in sorted(os.listdir("examples")) if not f.startswith("nosnap_")]


@pytest.mark.parametrize("directory", EXAMPLES)
def test_build(snapshot: SnapshotFixture, directory: str):
    with run_beet(directory=f"examples/{directory}") as ctx:
        assert snapshot("data_pack") == ctx.data
        assert snapshot("resource_pack") == ctx.assets
