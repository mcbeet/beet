import os
from typing import Any

import pytest

from beet import run_beet


@pytest.mark.parametrize("directory", os.listdir("tests/examples"))  # type: ignore
def test_build(snapshot: Any, directory: str):
    with run_beet(directory=f"tests/examples/{directory}") as ctx:
        assert snapshot("data_pack") == ctx.data
        assert snapshot("resource_pack") == ctx.assets
