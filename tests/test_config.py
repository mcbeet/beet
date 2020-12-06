import os
from typing import Any

import pytest

from beet.toolchain.config import load_config


@pytest.mark.parametrize("directory", os.listdir("tests/config_examples"))  # type: ignore
def test_config_resolution(snapshot: Any, directory: str):
    project_config = load_config(f"tests/config_examples/{directory}/beet.json")
    assert snapshot("json") == project_config.dict()
