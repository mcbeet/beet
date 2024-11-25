import os

import pytest
from pytest_insta import SnapshotFixture

from beet import run_beet


@pytest.mark.parametrize("directory", os.listdir("tests/ctx_config_examples"))
def test_examples(snapshot: SnapshotFixture, directory: str):
    with run_beet(directory=f"tests/ctx_config_examples/{directory}") as ctx:
        assert snapshot() == f'{ctx.meta["pytest"]}'
