import sys
from importlib import import_module
from pathlib import Path

import pytest
from pytest_insta import SnapshotFixture

EXAMPLES_DIRECTORY = Path(__file__).parent.parent / "examples"
sys.path.append(str(EXAMPLES_DIRECTORY))


@pytest.mark.parametrize(
    "module_name", [p.stem for p in EXAMPLES_DIRECTORY.glob("*.py")]
)
def test_output(
    snapshot: SnapshotFixture,
    capsys: pytest.CaptureFixture[str],
    module_name: str,
):
    import_module(module_name)
    assert snapshot() == capsys.readouterr().out
