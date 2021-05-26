import os

import pytest
from pytest_insta import SnapshotFixture

from beet import run_beet


@pytest.mark.parametrize("directory", os.listdir("examples"))
def test_build(snapshot: SnapshotFixture, directory: str):
    with run_beet(directory=f"examples/{directory}") as ctx:
        assert snapshot("data_pack") == ctx.data
        assert snapshot("resource_pack") == ctx.assets
