from beet import __version__
from beet.cli import beet


def test_version(runner):
    result = runner.invoke(beet, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output
