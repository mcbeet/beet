import pytest
from pytest_insta import SnapshotFixture
from beet.library.utils import modified_suffixes
from pathlib import Path


PATHS = [
    "load.mcfunction",
    ".mcfunction",
    "..mcfunction",
    "load.py.mcfunction",
    ".py.mcfunction",
    "aaa...mcfunction",
    "...mcfunction",
]


@pytest.mark.parametrize("path", PATHS)
def test_paths_suffixes(snapshot: SnapshotFixture, path: str):
    real_path = Path(path)
    assert snapshot(f"{path}.json") == {
        "path": path,
        "suffixes": list(real_path.suffixes),
        "modified_suffixes": list(modified_suffixes(real_path)),
    }
