import os
from pathlib import PurePath
from typing import Any

import pytest
from pytest_insta import SnapshotFixture

from beet import load_config


def encode_path(obj: Any) -> Any:
    if isinstance(obj, PurePath):
        return PurePath(os.path.relpath(obj)).as_posix()
    raise TypeError()


@pytest.mark.parametrize("directory", os.listdir("tests/config_examples"))
def test_config_resolution(snapshot: SnapshotFixture, directory: str):
    project_config = load_config(f"tests/config_examples/{directory}/beet.json")
    assert snapshot() == project_config.json(indent=2, encoder=encode_path) + "\n"
