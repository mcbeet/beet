import os

import pytest
from pytest_insta import SnapshotFixture

from beet.toolchain.config import load_config


@pytest.mark.parametrize("directory", os.listdir("tests/config_examples"))  # type: ignore
def test_config_resolution(snapshot: SnapshotFixture, directory: str):
    project_config = load_config(f"tests/config_examples/{directory}/beet.json")
    assert snapshot("beet-config") == project_config
