import os
from typing import Any

import pytest

from beet import Project, ProjectBuilder


@pytest.mark.parametrize("directory", os.listdir("tests/examples"))  # type: ignore
def test_build(snapshot: Any, directory: str):
    project = Project(config_directory=f"tests/examples/{directory}")
    ctx = ProjectBuilder(project).build()
    assert snapshot("data_pack") == ctx.data
    assert snapshot("resource_pack") == ctx.assets
