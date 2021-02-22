from pathlib import Path
from typing import Any

import pytest

from lectern import Document

EXAMPLES_DIRECTORY = Path(__file__, "../../examples").resolve()


@pytest.mark.parametrize(
    "path",
    [
        *sorted(EXAMPLES_DIRECTORY.glob("*.txt")),
        *sorted(EXAMPLES_DIRECTORY.glob("*.md")),
    ],
)
def test_load(snapshot: Any, path: Path):
    assert snapshot(path.stem + ".pack.txt") == Document(path=path)
